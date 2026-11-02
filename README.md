# BTC/ETH Wallet Generator

یک اسکریپت ساده پایتون برای ساخت کیف پول جدید با Seed دوازده‌کلمه‌ای BIP39، استخراج آدرس‌های بیت‌کوین و اتریوم، و نمایش موجودی آن‌ها از طریق APIهای بلاکچین.

## امکانات

- تولید Seed با ۱۲ کلمه BIP39
- استخراج آدرس BTC با مسیر `m/44'/0'/0'/0/0`
- استخراج آدرس ETH با مسیر `m/44'/60'/0'/0/0`
- دریافت موجودی بیت‌کوین از `blockchain.info`
- دریافت موجودی اتریوم از RPC عمومی `publicnode`
- نمایش Seed، آدرس‌ها و موجودی‌ها در خروجی

## پیش‌نیازها

- Python نسخه 3.10 تا 3.13 (روی 3.14 پکیج `coincurve` نصب نمی‌شود)
- اتصال به اینترنت

## نصب و اجرا

```bash
git clone https://github.com/USERNAME/btcfounder.git
cd btcfounder
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python btcf.py
```

اگر Python 3.12 روی سیستم نصب نیست، با `uv` هم می‌توانی اجرا کنی:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
uv venv --python 3.12 venv
source venv/bin/activate
uv pip install -r requirements.txt
python btcf.py
```

## نمونه خروجی

```text
Seed (12 words):
  word1 word2 word3 ... word12

BTC  (m/44'/0'/0'/0/0)
  Address: 1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  Balance: 0.00000000 BTC

ETH  (m/44'/60'/0'/0/0)
  Address: 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  Balance: 0.000000000000000000 ETH
```

## نکات امنیتی

- Seed کلید کامل کیف پول است. هرگز آن را با کسی به اشتراک نگذار و در جای عمومی منتشر نکن.
- این اسکریپت Seed را فقط روی صفحه نمایش می‌دهد و جایی ذخیره نمی‌کند.
- برای نگهداری مبلغ واقعی، از کیف پول سخت‌افزاری یا نرم‌افزارهای معتبر استفاده کن.

## وابستگی‌ها

- [bip_utils](https://github.com/ebellocchia/bip_utils)
- [requests](https://github.com/psf/requests)
