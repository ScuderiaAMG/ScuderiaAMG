from forex_python.converter import CurrencyRates

c = CurrencyRates()

print("简单货币换算器")

try:
    amount = float(input("请输入金额: "))
    from_currency = input("请输入源货币代码(如USD): ").upper()
    to_currency = input("请输入目标货币代码(如EUR): ").upper()

    exchange_rate = c.get_rate(from_currency, to_currency)
    result = amount * exchange_rate

    print(f"\n汇率: 1 {from_currency} = {exchange_rate:.4f} {to_currency}")
    print(f"{amount} {from_currency} = {result:.2f} {to_currency}")

except ValueError:
    print("金额输入有误，请输入数字。")
except Exception as e:
    print(f"发生错误：{e}")
    