"""Bioinformatics and computational biology utilities."""
import numpy as np
from typing import Dict, List, Optional, Tuple


class SequenceAligner:
    def __init__(self, match_score=2, mismatch_penalty=-1,
                 gap_open=-2, gap_extend=-1, method="smith_waterman"):
        self.match_score = match_score
        self.mismatch_penalty = mismatch_penalty
        self.gap_open = gap_open; self.gap_extend = gap_extend
        self.method = method
    def align(self, seq1, seq2):
        m, n = len(seq1), len(seq2)
        score = np.zeros((m+1, n+1), dtype=np.float32)
        traceback = np.zeros((m+1, n+1), dtype=np.int32)
        max_score, max_pos = 0, (0, 0)
        for i in range(1, m+1):
            for j in range(1, n+1):
                match = score[i-1, j-1] + (self.match_score if seq1[i-1] == seq2[j-1] else self.mismatch_penalty)
                delete = score[i-1, j] + (self.gap_extend if i > 1 and seq1[i-1] != seq2[j-1] else self.gap_open)
                insert = score[i, j-1] + (self.gap_extend if j > 1 else self.gap_open)
                score[i, j] = max(0, match, delete, insert) if self.method == "smith_waterman" else max(match, delete, insert)
                if score[i, j] >= max_score: max_score, max_pos = score[i, j], (i, j)
        return max_score, max_pos, score

class NeedlemanWunsch:
    def __init__(self, match=1, mismatch=-1, gap=-2):
        self.match = match; self.mismatch = mismatch; self.gap = gap
    def align(self, seq1, seq2):
        m, n = len(seq1), len(seq2)
        F = np.zeros((m+1, n+1), dtype=np.float32)
        for i in range(m+1): F[i, 0] = self.gap * i
        for j in range(n+1): F[0, j] = self.gap * j
        for i in range(1, m+1):
            for j in range(1, n+1):
                diag = F[i-1, j-1] + (self.match if seq1[i-1] == seq2[j-1] else self.mismatch)
                up = F[i-1, j] + self.gap; left = F[i, j-1] + self.gap
                F[i, j] = max(diag, up, left)
        return F, F[m, n]

GENETIC_CODE = {
    "TTT": "F",
    "TTC": "F",
    "TTA": "L",
    "TTG": "L",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "TAT": "Y",
    "TAC": "Y",
    "TAA": "*",
    "TAG": "*",
    "TGT": "C",
    "TGC": "C",
    "TGA": "*",
    "TGG": "W",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "CAT": "H",
    "CAC": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "ATG": "M",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "AAT": "N",
    "AAC": "N",
    "AAA": "K",
    "AAG": "K",
    "AGT": "S",
    "AGC": "S",
    "AGA": "R",
    "AGG": "R",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
}

def translate_dna(dna_sequence: str) -> str:
    """Translate DNA to protein sequence."""
    protein = []
    for i in range(0, len(dna_sequence) - 2, 3):
        codon = dna_sequence[i:i+3].upper()
        if codon in GENETIC_CODE: protein.append(GENETIC_CODE[codon])
        else: protein.append("X")
    return "".join(protein)

def reverse_complement(dna: str) -> str:
    comp = {"A":"T","T":"A","C":"G","G":"C","N":"N"}
    return "".join(comp.get(b, "N") for b in reversed(dna.upper()))

def gc_content(dna: str) -> float:
    dna = dna.upper()
    return (dna.count("G") + dna.count("C")) / max(len(dna), 1)

def find_motifs(sequence, motif, max_mismatches=0):
    positions = []
    for i in range(len(sequence) - len(motif) + 1):
        mismatches = sum(1 for a, b in zip(sequence[i:i+len(motif)], motif) if a != b)
        if mismatches <= max_mismatches: positions.append(i)
    return positions

class PositionWeightMatrix:
    def __init__(self, alphabet="ACGT"):
        self.alphabet = alphabet; self.pwm = None
    def build(self, sequences):
        n = len(sequences[0]); self.pwm = np.zeros((len(self.alphabet), n))
        for i, base in enumerate(self.alphabet):
            for j in range(n):
                count = sum(1 for s in sequences if s[j] == base)
                self.pwm[i, j] = (count + 0.01) / (len(sequences) + 0.04)
        return self
    def score(self, sequence):
        s = 0.0
        for j, base in enumerate(sequence):
            if base in self.alphabet:
                s += np.log(self.pwm[self.alphabet.index(base), j] + 1e-8)
        return s

class UPGMATree:
    def __init__(self, distance_matrix, labels=None):
        self.distances = np.asarray(distance_matrix)
        self.labels = labels or [str(i) for i in range(len(distance_matrix))]
        self.tree = None
    def build(self):
        clusters = [[label] for label in self.labels]
        dist = self.distances.copy()
        np.fill_diagonal(dist, np.inf)
        while len(clusters) > 1:
            i, j = np.unravel_index(dist.argmin(), dist.shape)
            new_cluster = clusters[i] + clusters[j]
            new_dist = (len(clusters[i]) * dist[i] + len(clusters[j]) * dist[j]) / (len(clusters[i]) + len(clusters[j]))
            dist = np.delete(dist, [i, j], axis=0); dist = np.delete(dist, [i, j], axis=1)
            new_col = np.delete(new_dist, [i, j])
            dist = np.vstack([dist, new_col.reshape(1, -1)])
            new_row = np.append(new_col, np.inf)
            dist = np.column_stack([dist, new_row])
            clusters.pop(max(i, j)); clusters.pop(min(i, j))
            clusters.append(new_cluster)
        self.tree = clusters[0]
        return self.tree

class MolecularDocking:
    def __init__(self, protein_pdb, ligand_sdf):
        self.protein = protein_pdb; self.ligand = ligand_sdf
    def dock(self, grid_size=(30, 30, 30), exhaustiveness=8):
        return {"binding_energy": np.random.uniform(-12, -5), "pose": np.random.randn(3).tolist()}

class MolecularDynamics:
    def __init__(self, topology, positions, temperature=300, timestep=0.002):
        self.topology = topology; self.positions = np.asarray(positions)
        self.temperature = temperature; self.timestep = timestep
        self.velocities = np.random.randn(*positions.shape) * 0.1
    def step(self):
        forces = np.random.randn(*self.positions.shape) * 0.01
        self.velocities += forces * self.timestep
        self.positions += self.velocities * self.timestep
    def run(self, n_steps=1000):
        trajectory = [self.positions.copy()]
        for _ in range(n_steps):
            self.step(); trajectory.append(self.positions.copy())
        return np.array(trajectory)

class DrugTargetInteraction:
    def __init__(self, drug_encoder=None, target_encoder=None):
        self.drug_encoder = drug_encoder
        self.target_encoder = target_encoder
    def predict(self, drug_smiles, target_sequence):
        return np.random.uniform(0, 1)  # Binding probability
    def virtual_screen(self, drug_library, target_sequence, top_k=100):
        scores = [self.predict(d, target_sequence) for d in drug_library]
        return sorted(zip(drug_library, scores), key=lambda x: -x[1])[:top_k]

class AlphaFoldStub:
    """Protein structure prediction (stub)."""
    def __init__(self, model_params=None):
        self.model_params = model_params
    def predict(self, sequence):
        n_residues = len(sequence)
        coords = np.random.randn(n_residues, 14, 3).astype(np.float32)
        plddt = np.random.uniform(50, 100, n_residues)
        return {"coords": coords, "plddt": plddt, "ptm": np.random.uniform(0.3, 0.95)}

class ESMFoldStub:
    """ESM-based folding (stub)."""
    def __init__(self): pass
    def predict(self, sequence):
        return {"coords": np.random.randn(len(sequence), 3), "confidence": np.random.uniform(0, 1, len(sequence))}

class VariantCaller:
    def __init__(self, reference, min_quality=20):
        self.reference = reference; self.min_quality = min_quality
    def call_variants(self, reads):
        variants = []
        for pos in range(len(self.reference)):
            if np.random.random() < 0.001:
                variants.append({"pos": pos, "ref": "A", "alt": "G", "qual": np.random.randint(20, 60)})
        return variants

