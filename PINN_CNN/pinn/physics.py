"""Physics-informed loss functions for battery SOH estimation.

Three physics constraints are enforced during training:
  1. ECM resistance consistency  — predicted SOH must match measurable R_int growth
  2. Degradation smoothness      — adjacent cycles of the same cell degrade smoothly
  3. Monotonicity                — SOH is non-increasing across cycles (convex penalty)
"""
import torch
import torch.nn as nn


class PhysicsLoss(nn.Module):
    """Composite physics-informed loss with configurable component weights."""

    def __init__(self, config):
        super().__init__()
        p = config.physics
        self.lambda_ecm = p.ecm_weight
        self.lambda_smooth = p.smoothness_weight
        self.lambda_mono = p.monotonic_weight
        self.r0_init = p.r0_initial_ohm
        self.r0_coeff = p.r0_aging_coeff
        self.alpha = p.degradation_alpha

    def ecm_resistance_loss(
        self, soh_pred: torch.Tensor, dv_measured: torch.Tensor
    ) -> torch.Tensor:
        """ECM consistency: measured dV/I should match resistance model at predicted SOH.

        Physics:  R_int(SOH) = R0_init * (1 + beta * (1 - SOH))
                  Loss = MSE(dV_measured, R_int(SOH_pred))

        dv_measured = voltage-step at charge start / charge current (ohm proxy).
        """
        r_predicted = self.r0_init * (1.0 + self.r0_coeff * (1.0 - soh_pred))
        return nn.functional.mse_loss(r_predicted, dv_measured)

    def degradation_smoothness_loss(
        self, soh_pred: torch.Tensor, cell_ids: torch.Tensor, cycles: torch.Tensor
    ) -> torch.Tensor:
        """Penalise non-smooth SOH trajectories within the same cell.

        For each cell, the local second-difference of SOH vs cycle should be small.
        """
        total_loss = 0.0
        n_cells = 0
        unique_cells = torch.unique(cell_ids)

        for cid in unique_cells:
            mask = cell_ids == cid
            if mask.sum() < 3:
                continue
            # sort by cycle
            cyc_cell = cycles[mask]
            soh_cell = soh_pred[mask].squeeze(-1)
            sort_idx = torch.argsort(cyc_cell)
            soh_sorted = soh_cell[sort_idx]

            # second-difference:  SOH_{n+1} - 2*SOH_n + SOH_{n-1}
            second_diff = soh_sorted[2:] - 2 * soh_sorted[1:-1] + soh_sorted[:-2]
            if torch.isnan(second_diff).any() or torch.isinf(second_diff).any():
                continue  # skip corrupted cells
            total_loss += (second_diff ** 2).mean()
            n_cells += 1

        return total_loss / max(n_cells, 1)

    def monotonicity_loss(
        self, soh_pred: torch.Tensor, cell_ids: torch.Tensor, cycles: torch.Tensor
    ) -> torch.Tensor:
        """Soft penalty: SOH should be non-increasing across cycles.

        Loss = mean(ReLU(SOH_{n+1} - SOH_n)) per cell.
        Uses a small tolerance (1e-3) to allow measurement noise.
        """
        total_loss = 0.0
        n_pairs = 0
        unique_cells = torch.unique(cell_ids)

        for cid in unique_cells:
            mask = cell_ids == cid
            if mask.sum() < 2:
                continue
            cyc_cell = cycles[mask]
            soh_cell = soh_pred[mask].squeeze(-1)
            sort_idx = torch.argsort(cyc_cell)
            soh_sorted = soh_cell[sort_idx]

            # penalize any increase beyond tolerance
            delta = soh_sorted[1:] - soh_sorted[:-1]
            violation = torch.clamp(delta + 1e-3, min=0.0)
            total_loss += violation.mean()
            n_pairs += 1

        return total_loss / max(n_pairs, 1)

    def forward(
        self,
        soh_pred: torch.Tensor,
        dv_measured: torch.Tensor,
        cell_ids: torch.Tensor,
        cycles: torch.Tensor,
    ) -> tuple[torch.Tensor, dict]:
        """Compute total physics loss and per-component breakdown.

        Args:
            soh_pred:    (B, 1) predicted SOH
            dv_measured: (B, 1) measured dV_start / I  (ohm proxy)
            cell_ids:    (B,)   integer cell identifiers
            cycles:      (B, 1) cycle numbers

        Returns:
            total_loss:  scalar tensor
            components:  dict of {name: scalar float} for logging
        """
        l_ecm = self.ecm_resistance_loss(soh_pred, dv_measured)
        l_smooth = self.degradation_smoothness_loss(soh_pred, cell_ids, cycles)
        l_mono = self.monotonicity_loss(soh_pred, cell_ids, cycles)

        total = (
            self.lambda_ecm * l_ecm
            + self.lambda_smooth * l_smooth
            + self.lambda_mono * l_mono
        )

        components = {
            "phys_ecm": l_ecm.item(),
            "phys_smooth": l_smooth.item(),
            "phys_mono": l_mono.item(),
            "phys_total": total.item(),
        }
        return total, components
