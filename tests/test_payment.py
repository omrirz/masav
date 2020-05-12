import pytest


@pytest.fixture()
def institute():
    from masav import MasavPayingInstitute

    mpi = MasavPayingInstitute(
        institute_code=12345678,
        institute_name="Company ISRAEL LTD.",
        sending_institute_code=98765,
    )
    return mpi


@pytest.fixture()
def payments_list():
    from masav import MasavPaymentDetails

    mpd1 = MasavPaymentDetails(
        amount=85,
        bank_number="11",
        branch_number="303",
        account_number="007008629",
        payee_id="000000000",
        payee_name="Leto II Atreides",
        payee_number="00000000000001313131",
    )
    mpd2 = MasavPaymentDetails(
        amount=1346.37,
        bank_number="31",
        branch_number="051",
        account_number="000283487",
        payee_id="123456782",
        payee_name="Thorin Oakenshield",
        payee_number="00000000000001122233",
    )
    mpd3 = MasavPaymentDetails(
        amount=689.5,
        bank_number="13",
        branch_number="152",
        account_number="001497016",
        payee_id="000000000",
        payee_name="Long Name With More Than 16 Letters",
        payee_number="00000000000001928370",
    )
    payments_list = [mpd1, mpd2, mpd3]
    return payments_list


def test_file_creation(institute, payments_list):
    file = "tests/payment_file_generated_by_test.bin"
    institute.create_payment_file(
        file=file,
        payments_list=payments_list,
        payment_date="200507",
        serial_number=404,
        creation_date="200507",
    )
    with open(file, "rb") as f:
        data = f.read()
    with open("tests/masav_file_example.bin", "rb") as f:
        expected_data = f.read()

    assert data == expected_data
