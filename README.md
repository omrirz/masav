# Python API for Israeli Masav payments

## Install

```console
pip install masav
```

## Usage

### from JSON

```python
# TODO
```

### low level API

```python
from masav import MasavPayingInstitute, MasavPaymentDetails

institute = MasavPayingInstitute(
    institute_code=12345678,
    institute_name="Company ISRAEL LTD.",
    sending_institute_code=12345
    )

payee_details_1 = MasavPaymentDetails(
    amount=85,
    bank_number="11",
    branch_number="303",
    account_number="007008629",
    payee_id="123123127",
    payee_name="Leto II Atreides",
    payee_number="00000000000001313131"
    )

payee_details_2 = MasavPaymentDetails(
    amount=1346.37,
    bank_number="31",
    branch_number="051",
    account_number="000283487",
    payee_id="123456782",
    payee_name="Thorin Oakenshield",
    payee_number="00000000000001122233"
    )

payments_list = [payee_details_1, payee_details_2]

file = "tests/payment_file_generated_by_test.bin"
institute.create_payment_file(
        file=file,
        payments_list=payments_list,
        payment_date="200507",
        serial_number=404,
        creation_date="200507"
    )
```

## Development

```console
git clone https://github.com/omrirz/masav.git
cd masav
pip install -r requirements.txt
```

## Test

```console
tox
```
