import requests

print("简单货币换算器")

try:
    amount = float(input("请输入金额: "))
    from_currency = input("请输入源货币代码(如USD): ").upper()
    to_currency = input("请输入目标货币代码(如EUR): ").upper()

    url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    exchange_rate = data['rates'][to_currency] / amount
    result = data['rates'][to_currency]

    print(f"\n汇率: 1 {from_currency} = {exchange_rate:.4f} {to_currency}")
    print(f"{amount} {from_currency} = {result:.2f} {to_currency}")

except ValueError:
    print("金额输入有误，请输入数字。")
except Exception as e:
    print(f"发生错误：{e}")