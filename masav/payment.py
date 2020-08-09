"""
A (much) nicer API to build Masav payments file

Based on this API
https://www.masav.co.il/media/1987/mifrat_zikuim_msv.pdf
https://www.masav.co.il/media/2001/hebrew.pdf

Note: Most of the inputs to the ctor and to create_payment_file are Union[int, str].
This is because there are many fields such as payee_id that can have leading zeros.
Either way we cast them to str and pad them with leading zeros according to the spec.
The rest of the field are dates in format of YYMMDD or YYMM ot datetime.datetime.
"""

from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Union, Optional

YYMMDD = Union[str, datetime]
YYMM = Union[str, datetime]
PathLike = Union[Path, str]
PaymentLine = bytes
MasavFileLine = bytes

RECORD_LEN = 128
NEWLINE = "\r\n"
ENCODING = "ascii"


def _normalize_date(date: Union[YYMMDD, YYMM, datetime], fmt: str = "YYMMDD"):
    if isinstance(date, datetime):
        if fmt == "YYMMDD":
            return date.strftime("%y%m%d")
        else:
            return date.strftime("%y%m")
    else:
        return date


class MasavPaymentError(Exception):
    pass


class MasavPaymentDetails:
    def __init__(
        self,
        amount: Union[float, int],
        bank_number: Union[int, str],
        branch_number: Union[int, str],
        account_number: Union[int, str],
        payee_id: Union[int, str],
        payee_name: str,
        payee_number: Union[int, str],
        payed_for_from: YYMM = "0000",
        payed_for_until: YYMM = "0000",
    ):
        self.amount: Union[float, int] = amount
        self.bank_number: str = f"{int(str(bank_number)[:2]):02d}"
        self.branch_number: str = f"{int(str(branch_number)[:3]):03d}"
        self.account_number: str = f"{int(str(account_number)[:9]):09d}"
        self.payee_id: str = f"{int(str(payee_id)[:9]):09d}"
        self.payee_name: str = f"{payee_name[:16]:>16}"
        self.payee_number: str = f"{int(str(payee_number)[:20]):020d}"
        self.payed_for_from: YYMM = _normalize_date(payed_for_from, fmt="YYMM")
        self.payed_for_until: YYMM = _normalize_date(payed_for_until, fmt="YYMM")


class MasavPayingInstitute:
    def __init__(
        self,
        institute_code: Union[int, str],
        institute_name: Union[int, str],
        sending_institute_code: Union[int, str],
    ):
        institute_code = f"{int(str(institute_code)[:8]):08d}"
        institute_name = f"{str(institute_name)[:30]:>30}"
        sending_institute_code = f"{int(str(sending_institute_code)[:5]):05d}"
        if len(institute_code) > 8:
            raise MasavPaymentError(
                "institute_code must be an integer with 8 digits at most."
            )
        if len(sending_institute_code) > 5:
            raise MasavPaymentError(
                "sending_institute_code must be an integer with 5 digits at most."
            )
        self.institute_code: str = institute_code
        self.institute_name: str = institute_name
        self.sending_institute_code: str = sending_institute_code

    def create_payment_file(
        self,
        file: PathLike,
        payments_list: List[MasavPaymentDetails],
        payment_date: YYMMDD,
        serial_number: Union[int, str],
        creation_date: YYMMDD,
        coin: Optional[Union[int, str]] = "00",
    ):
        file, payment_date, creation_date, serial_number, coin = self._normalize_data(
            file=file,
            payment_date=payment_date,
            creation_date=creation_date,
            serial_number=serial_number,
            coin=coin,
        )
        file_content = self._build_payment_data(
            payments_list=payments_list,
            payment_date=payment_date,
            serial_number=serial_number,
            creation_date=creation_date,
            coin=coin,
        )
        self._save_content_to_file(file=file, file_content=file_content)

    @staticmethod
    def _normalize_data(
        file: PathLike,
        payment_date: YYMMDD,
        creation_date: YYMMDD,
        serial_number: Union[int, str],
        coin: Union[int, str],
    ):

        if isinstance(file, str):
            file = Path(file)
        creation_date = _normalize_date(creation_date, fmt="YYMMDD")
        payment_date = _normalize_date(payment_date, fmt="YYMMDD")

        if len(creation_date) != 6:
            raise MasavPaymentError(
                "creation_date must be a date.\n"
                "Pass in a string in format YYMMDD or datetime.datetime object"
            )
        if len(payment_date) != 6:
            raise MasavPaymentError(
                "payment_date must be a date.\n"
                "Pass in a string in format YYMMDD or datetime.datetime object"
            )
        serial_number = f"{int(str(serial_number)[:3]):03d}"
        coin = f"{int(str(coin)[:2]):02d}"
        return file, payment_date, creation_date, serial_number, coin

    def _build_payment_data(
        self,
        payments_list: List[MasavPaymentDetails],
        payment_date: YYMMDD,
        serial_number: str,
        creation_date: YYMMDD,
        coin: str,
    ) -> List[MasavFileLine]:

        header = self._build_header(
            creation_date=creation_date,
            payment_date=payment_date,
            serial_number=serial_number,
            coin=coin,
        )

        payload, payments_sum, number_of_payments = self._build_payload(
            payments_list=payments_list, coin=coin
        )

        footer = self._build_footer(
            payment_date=payment_date,
            payments_sum=payments_sum,
            number_of_payments=number_of_payments,
            serial_number=serial_number,
            coin=coin,
        )
        last_line = self._build_file_last_line()

        return [header] + payload + [footer] + [last_line]

    @staticmethod
    def _save_content_to_file(file: Path, file_content: List[MasavFileLine]) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("wb") as f:
            for line in file_content:
                f.write(line)

    def _build_header(
        self, creation_date: YYMMDD, payment_date: YYMMDD, serial_number: str, coin: str
    ) -> MasavFileLine:
        header = (
            f"K{self.institute_code}{coin}{payment_date}"
            f"{0}{serial_number}{0}{creation_date}{self.sending_institute_code}"
            f"{'0' * 6}{self.institute_name}{' ' * 56}KOT{NEWLINE}"
        ).encode(ENCODING)
        return header

    def _build_payload(
        self, payments_list: List[MasavPaymentDetails], coin: str
    ) -> Tuple[List[PaymentLine], int, int]:
        payload = []
        payments_sum = 0
        number_of_payments = 0
        for payment in payments_list:
            if payment.amount <= 0:
                continue
            payment_sum_fraction = f"{payment.amount % 1:2.02f}"[2:]
            p = (
                f"1{self.institute_code}{coin}{'0' * 6}"
                f"{payment.bank_number}{payment.branch_number}"
                f"{'0000'}{payment.account_number}"
                f"0{payment.payee_id}{payment.payee_name}"
                f"{int(payment.amount):011d}{payment_sum_fraction}"
                f"{payment.payee_number}{payment.payed_for_from}"
                f"{payment.payed_for_until}"
                f"000{'006'}{'0' * 18}{' ' * 2}{NEWLINE}"
            ).encode(ENCODING)
            payload.append(p)
            payments_sum += payment.amount
            number_of_payments += 1

        return payload, payments_sum, number_of_payments

    def _build_footer(
        self,
        payment_date: YYMMDD,
        payments_sum: Union[float, int],
        number_of_payments: int,
        serial_number: str,
        coin: str,
    ) -> MasavFileLine:
        payment_sum_fraction = f"{payments_sum % 1:2.02f}"[2:]
        footer = (
            f"5{self.institute_code}{coin}{payment_date}"
            f"{0}{serial_number}{int(payments_sum):013d}{payment_sum_fraction}"
            f"{'0' * 15}{int(number_of_payments):07d}{'0' * 7}"
            f"{' ' * 63}{NEWLINE}"
        ).encode(ENCODING)
        return footer

    @staticmethod
    def _build_file_last_line() -> bytes:
        return f"{'9' * RECORD_LEN}".encode(ENCODING)

    def _split_payments_into_banks(self):
        raise NotImplementedError
