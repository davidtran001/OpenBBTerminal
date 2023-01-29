""" Futures Controller """
__docformat__ = "numpy"

# pylint:disable=too-many-lines

import argparse
import logging
from datetime import datetime, timedelta
from typing import List

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.fixedincome import ecb_view, nyfed_view, oecd_view
from openbb_terminal.fixedincome import fred_view

from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    valid_date,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.menu import session

logger = logging.getLogger(__name__)


class FixedIncomeController(BaseController):
    """Fixed Income Controller class"""

    CHOICES_COMMANDS = [
        "estr",
        "sofr",
        "sonia",
        "ameribor",
        "ffer",
        "fftr",
        "effr",
        "obfr",
        "iorb",
        "projection",
        "oldprojection",
        "dwpcr",
        "ecbdfr",
        "ecbmlfr",
        "ecbmrofr",
        "stir",
        "ltir",
        "tmc",
        "ffrmc",
        "ycrv",
        "iiycrv",
        "ecbycrv",
    ]

    PATH = "/fixedincome/"
    CHOICES_GENERATION = True

    estr_parameter_to_fred_id = {
        "volume_weighted_trimmed_mean_rate": "ECBESTRVOLWGTTRMDMNRT",
        "total_volume": "ECBESTRTOTVOL",
        "number_of_transactions": "ECBESTRNUMTRANS",
        "rate_at_75th_percentile_of_volume": "ECBESTRRT75THPCTVOL",
        "number_of_active_banks": "ECBESTRNUMACTBANKS",
        "share_of_volume_of_the_5_largest_active_banks": "ECBESTRSHRVOL5LRGACTBNK",
        "rate_at_25th_percentile_of_volume": "ECBESTRRT25THPCTVOL",
    }
    estr_parameter_to_ecb_id = {
        "volume_weighted_trimmed_mean_rate": "EST.B.EU000A2X2A25.WT",
        "total_volume": "EST.B.EU000A2X2A25.TT",
        "number_of_transactions": "EST.B.EU000A2X2A25.NT",
        "rate_at_75th_percentile_of_volume": "EST.B.EU000A2X2A25.R75",
        "number_of_active_banks": "EST.B.EU000A2X2A25.NB",
        "share_of_volume_of_the_5_largest_active_banks": "EST.B.EU000A2X2A25.VL",
        "rate_at_25th_percentile_of_volume": "EST.B.EU000A2X2A25.R25",
    }
    sofr_parameter_to_fred_id = {
        "overnight": "SOFR",
        "30_day": "SOFR30DAYAVG",
        "90_day": "SOFR90DAYAVG",
        "180_day": "SOFR180DAYAVG",
        "index": "SOFRINDEX",
    }
    sonia_parameter_to_fred_id = {
        "rate": "IUDSOIA",
        "index": "IUDZOS2",
        "10th_percentile": "IUDZLS6",
        "25th_percentile": "IUDZLS7",
        "75th_percentile": "IUDZLS8",
        "90th_percentile": "IUDZLS9",
        "total_nominal_value": "IUDZLT2",
    }
    ameribor_parameter_to_fred_id = {
        "overnight": "AMERIBOR",
        "term_30": "AMBOR30T",
        "term_90": "AMBOR90T",
        "1_week_term_structure": "AMBOR1W",
        "1_month_term_structure": "AMBOR1M",
        "3_month_term_structure": "AMBOR3M",
        "6_month_term_structure": "AMBOR6M",
        "1_year_term_structure": "AMBOR1Y",
        "2_year_term_structure": "AMBOR2Y",
        "30_day_ma": "AMBOR30",
        "90_day_ma": "AMBOR90",
    }
    ffer_parameter_to_fred_id = {
        "monthly": "FEDFUNDS",
        "daily": "DFF",
        "weekly": "FF",
        "daily_excl_weekend": "RIFSPFFNB",
        "annual": "RIFSPFFNA",
        "biweekly": "RIFSPFFNBWAW",
    }
    effr_parameter_to_fred_id = {
        "rate": "EFFR",
        "volume": "EFFRVOL",
        "1th_percentile": "EFFR1",
        "25th_percentile": "EFFR25",
        "75th_percentile": "EFFR75",
        "99th_percentile": "EFFR99",
    }
    effr_parameter_to_nyfed_id = {
        "rate": "percentRate",
        "volume": "volumeInBillions",
        "1th_percentile": "percentPercentile1",
        "25th_percentile": "percentPercentile25",
        "75th_percentile": "percentPercentile75",
        "99th_percentile": "percentPercentile99",
    }
    obfr_parameter_to_fred_id = {
        "rate": "OBFR",
        "volume": "OBFRVOL",
        "1th_percentile": "EFFR1",
        "25th_percentile": "EFFR25",
        "75th_percentile": "EFFR75",
        "99th_percentile": "EFFR99",
    }
    dwpcr_parameter_to_fred_id = {
        "daily_excl_weekend": "DPCREDIT",
        "monthly": "MPCREDIT",
        "weekly": "WPCREDIT",
        "daily": "RIFSRPF02ND",
        "annual": "RIFSRPF02NA",
    }
    tmc_parameter_to_fred_id = {
        "3_month": "T10Y3M",
        "2_year": "T10Y2Y",
    }
    ffrmc_parameter_to_fred_id = {
        "10_year": "T10YFF",
        "5_year": "T5YFF",
        "1_year": "T1YFF",
        "6_month": "T6MFF",
    }

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(self.choices)  # type: ignore

    def print_help(self):
        """Print help"""
        mt = MenuText("fixedincome/")
        mt.add_info("_reference_rates_")
        mt.add_cmd("estr")
        mt.add_cmd("sofr")
        mt.add_cmd("sonia")
        mt.add_cmd("ameribor")
        mt.add_raw("\n")
        mt.add_info("_central_bank_rates_")
        mt.add_cmd("ffer")
        mt.add_cmd("fftr")
        mt.add_cmd("effr")
        mt.add_cmd("obfr")
        mt.add_cmd("iorb")
        mt.add_cmd("projection")
        mt.add_cmd("oldprojection")
        mt.add_cmd("dwpcr")
        mt.add_cmd("ecbdfr")
        mt.add_cmd("ecbmlfr")
        mt.add_cmd("ecbmrofr")
        mt.add_cmd("stir")
        mt.add_cmd("ltir")
        mt.add_raw("\n")
        mt.add_info("_constant_maturities_spreads_")
        mt.add_cmd("tmc")
        mt.add_cmd("ffrmc")
        mt.add_raw("\n")
        mt.add_info("_yield_curves_")
        mt.add_cmd("ycrv")
        mt.add_cmd("iiycrv")
        mt.add_cmd("ecbycrv")

        console.print(text=mt.menu_text, menu="Fixed Income")

    @log_start_end(log=logger)
    def call_estr(self, other_args: List[str]):
        """Process estr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="estr",
            description="Get Euro Short-Term Rate data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Euro Short-Term Rate data to retrieve",
            default="volume_weighted_trimmed_mean_rate",
            choices=list(self.estr_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.source == "FRED":
                fred_view.plot_estr(
                    self.estr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "ECB":
                ecb_view.plot_estr(
                    self.estr_parameter_to_ecb_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_sofr(self, other_args: List[str]):
        """Process sofr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sofr",
            description="Get Secured Overnight Financing Rate (SOFR) data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific SOFR data to retrieve",
            default="overnight",
            choices=list(self.sofr_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.source == "FRED":
                fred_view.plot_sofr(
                    self.sofr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_sofr(
                    ns_parser.parameter,
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_sonia(self, other_args: List[str]):
        """Process sonia command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sonia",
            description="Get Sterling Overnight Index Average (SONIA) data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific SONIA data to retrieve",
            default="rate",
            choices=list(self.sonia_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_sonia(
                self.sonia_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ameribor(self, other_args: List[str]):
        """Process ameribor command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ameribor",
            description="Get American Interbank Offered Rate (AMERIBOR) data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific AMERIBOR data to retrieve",
            default="overnight",
            choices=list(self.ameribor_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ameribor(
                self.ameribor_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ffer(self, other_args: List[str]):
        """Process ffer command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ffer",
            description="Get Federal Funds Effective Rate data\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Federal Funds Effective Rate data to retrieve",
            default="monthly",
            choices=list(self.ffer_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ffer(
                self.ffer_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_fftr(self, other_args: List[str]):
        """Process fftr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fftr",
            description="Get Federal Funds Target Range data.\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.source == "FRED":
                fred_view.plot_fftr(
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_fftr(
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_effr(self, other_args: List[str]):
        """Process effr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="effr",
            description="Get Effective Federal Funds Rate data.\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Effective Federal Funds Rate data to retrieve",
            default="rate",
            choices=list(self.effr_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.source == "FRED":
                fred_view.plot_effr(
                    self.effr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_effr(
                    self.effr_parameter_to_nyfed_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_obfr(self, other_args: List[str]):
        """Process obfr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="obfr",
            description="Get Overnight Bank Funding Rate data.\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Overnight Bank Funding Rate data to retrieve",
            default="rate",
            choices=list(self.obfr_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.source == "FRED":
                fred_view.plot_obfr(
                    self.obfr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_obfr(
                    self.effr_parameter_to_nyfed_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_iorb(self, other_args: List[str]):
        """Process iorb command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="iorb",
            description="Get Interest Rate on Reserve Balances data\nA bank rate is the interest rate a nation's "
            "central bank charges to its domestic banks to borrow money. The rates central banks charge "
            "are set to stabilize the economy. In the United States, the Federal Reserve System's Board "
            "of Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_iorb(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_projection(self, other_args: List[str]):
        """Process projection command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="projection",
            description="Get FOMC Summary of Economic Projections for the Fed Funds Rate.\nA bank rate is the "
            "interest rate a nation's central bank charges to its domestic banks to borrow money. The "
            "rates central banks charge are set to stabilize the economy. In the United States, "
            "the Federal Reserve System's Board of Governors set the bank rate, also known as the "
            "discount rate.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_projection(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_oldprojection(self, other_args: List[str]):
        """Process oldprojection command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="oldprojection",
            description="Get Longer Run FOMC Summary of Economic Projections for the Fed Funds Rate.\nA bank rate is "
            "the interest rate a nation's central bank charges to its domestic banks to borrow money. The "
            "rates central banks charge are set to stabilize the economy. In the United States, "
            "the Federal Reserve System's Board of Governors set the bank rate, also known as the "
            "discount rate.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_oldprojection(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_dwpcr(self, other_args: List[str]):
        """Process dwpcr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dwpcr",
            description="Get Discount Window Primary Credit Rate data.\nA bank rate is the interest rate a nation's "
            "central bank charges to its domestic banks to borrow money. The rates central banks charge "
            "are set to stabilize the economy. In the United States, the Federal Reserve System's Board "
            "of Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Discount Window Primary Credit Rate data to retrieve",
            default="daily_excl_weekend",
            choices=list(self.dwpcr_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_dwpcr(
                self.dwpcr_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ecbdfr(self, other_args: List[str]):
        """Process ecbdfr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ecbdfr",
            description="Plot ECB Deposit Facility Rate for Euro Area. The deposit facility rate is one of the three "
            "interest rates the ECB sets every six weeks as part of its monetary policy. The rate defines "
            "the interest banks receive for depositing money with the central bank overnight. A bank rate "
            "is the interest rate a nation's central bank charges to its domestic banks to borrow money. "
            "The rates central banks charge are set to stabilize the economy.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ecbdfr(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ecbmlfr(self, other_args: List[str]):
        """Process ecbmlfr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ecbmlfr",
            description="Plot ECB Deposit Facility Rate for Euro Area. A standing facility of the Euro-system which "
            "counterparties may use to receive overnight credit from a national central bank at a "
            "pre-specified interest rate against eligible assets. A bank rate "
            "is the interest rate a nation's central bank charges to its domestic banks to borrow money. "
            "The rates central banks charge are set to stabilize the economy.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ecbmlfr(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ecbmrofr(self, other_args: List[str]):
        """Process ecbmrofr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ecbmrofr",
            description="Plot ECB Main Refinancing Operations Rate: Fixed Rate Tenders for Euro Area. A regular open "
            "market operation executed by the Euro-system (in the form of a reverse transaction) for the "
            "purpose of providing the banking system with the amount of liquidity that the former deems "
            "to be appropriate. Main refinancing operations are conducted through weekly standard tenders "
            "(in which banks can bid for liquidity) and normally have a maturity of one week. A bank rate "
            "is the interest rate a nation's central bank charges to its domestic banks to borrow money. "
            "The rates central banks charge are set to stabilize the economy.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ecbmrofr(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_stir(self, other_args: List[str]):
        """Process stir command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="str",
            description='Plot short term interest rates from selected countries. \nShort-term interest rates are the rates at which short-term borrowings are effected between financial institutions or the rate at which short-term government paper is issued or traded in the market. Short-term interest rates are generally averages of daily rates, measured as a percentage. Short-term interest rates are based on three-month money market rates where available. Typical standardised names are "money market rate" and "treasury bill rate".',
        )
        parser.add_argument(
            "-c",
            "--country",
            type=str,
            action="store",
            nargs="+",
            dest="countries",
            help="Countries to get data for.",
            default=["USA"],
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=None,
        )
        parser.add_argument(
            "--forecast",
            action="store_true",
            dest="forecast",
            default=False,
            help="If True, plot forecasts for short term interest rates",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            oecd_view.plot_short_term_interest_rate(
                countries=ns_parser.countries,
                forecast=ns_parser.forecast,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ltir(self, other_args: List[str]):
        """Process ltir command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="str",
            description="Plot long term interest rates from selected countries. \nLong-term interest rates refer to government bonds maturing in ten years. Rates are mainly determined by the price charged by the lender, the risk from the borrower and the fall in the capital value. Long-term interest rates are generally averages of daily rates, measured as a percentage. These interest rates are implied by the prices at which the government bonds are traded on financial markets, not the interest rates at which the loans were issued. In all cases, they refer to bonds whose capital repayment is guaranteed by governments. Long-term interest rates are one of the determinants of business investment. Low long-term interest rates encourage investment in new equipment and high interest rates discourage it. Investment is, in turn, a major source of economic growth.",
        )
        parser.add_argument(
            "-c",
            "--country",
            type=str,
            action="store",
            nargs="+",
            dest="countries",
            help="Countries to get data for, use three letter country codes.",
            default=["USA"],
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=None,
        )
        parser.add_argument(
            "--forecast",
            action="store_true",
            dest="forecast",
            default=False,
            help="If True, plot forecasts for long term interest rates",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            oecd_view.plot_long_term_interest_rate(
                countries=ns_parser.countries,
                forecast=ns_parser.forecast,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_tmc(self, other_args: List[str]):
        """Process tmc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tmc",
            description="Get 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity data. "
            "Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values "
            "of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis "
            "through interpolation of the Treasury yield curve which, in turn, is based on closing "
            "bid-yields of actively-traded Treasury securities.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected treasury constant maturity to subtract",
            default="3_month",
            choices=list(self.tmc_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_tmc(
                self.tmc_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ffrmc(self, other_args: List[str]):
        """Process ffrmc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ffrmc",
            description="Get Selected Treasury Constant Maturity Minus Federal Funds Rate. "
            "Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values "
            "of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis "
            "through interpolation of the Treasury yield curve which, in turn, is based on closing "
            "bid-yields of actively-traded Treasury securities.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected Treasury Constant Maturity",
            default="10_year",
            choices=list(self.ffrmc_parameter_to_fred_id.keys()),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ffrmc(
                self.ffrmc_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ycrv(self, other_args: List[str]):
        """Process ycrv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ycrv",
            description="Generate US yield curve. \nThe yield curve shows the bond rates"
            "at different maturities.\nThe graphic depiction of the relationship between the yield on bonds of the "
            "same credit quality but different maturities is known as the yield curve. In the past, "
            "most market participants have constructed yield curves from the observations of prices and "
            "yields in the Treasury market. Two reasons account for this tendency. First, "
            "Treasury securities are viewed as free of default risk, and differences in creditworthiness "
            "do not affect yield estimates. Second, as the most active bond market, the Treasury market "
            "offers the fewest problems of illiquidity or infrequent trading. The key function of the "
            "Treasury yield curve is to serve as a benchmark for pricing bonds and setting yields in "
            "other sectors of the debt market.\nIt is clear that the market’s expectations of future rate "
            "changes are one important determinant of the yield-curve shape. For example, "
            "a steeply upward-sloping curve may indicate market expectations of near-term Fed tightening "
            "or of rising inflation. However, it may be too restrictive to assume that the yield "
            "differences across bonds with different maturities only reflect the market’s rate "
            "expectations. The well-known pure expectations hypothesis has such an extreme implication. "
            "The pure expectations hypothesis asserts that all government bonds have the same near-term "
            "expected return (as the nominally riskless short-term bond) because the return-seeking "
            "activity of risk-neutral traders removes all expected return differentials across bonds.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=valid_date,
            help="Date to get data from FRED. If not supplied, the most recent entry will be used.",
            dest="date",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:

            fred_view.display_yield_curve(
                date=ns_parser.date.strftime("%Y-%m-%d") if ns_parser.date else "",
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_iiycrv(self, other_args: List[str]):
        """Process iiycrv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="iiycrv",
            description="Generate US inflation-indexed yield curve. \nThe yield curve shows the bond rates"
            "at different maturities.\nThe graphic depiction of the relationship between the yield on bonds of the "
            "same credit quality but different maturities is known as the yield curve. In the past, "
            "most market participants have constructed yield curves from the observations of prices and "
            "yields in the Treasury market. Two reasons account for this tendency. First, "
            "Treasury securities are viewed as free of default risk, and differences in creditworthiness "
            "do not affect yield estimates. Second, as the most active bond market, the Treasury market "
            "offers the fewest problems of illiquidity or infrequent trading. The key function of the "
            "Treasury yield curve is to serve as a benchmark for pricing bonds and setting yields in "
            "other sectors of the debt market.\nIt is clear that the market’s expectations of future rate "
            "changes are one important determinant of the yield-curve shape. For example, "
            "a steeply upward-sloping curve may indicate market expectations of near-term Fed tightening "
            "or of rising inflation. However, it may be too restrictive to assume that the yield "
            "differences across bonds with different maturities only reflect the market’s rate "
            "expectations. The well-known pure expectations hypothesis has such an extreme implication. "
            "The pure expectations hypothesis asserts that all government bonds have the same near-term "
            "expected return (as the nominally riskless short-term bond) because the return-seeking "
            "activity of risk-neutral traders removes all expected return differentials across bonds.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=valid_date,
            help="Date to get data from FRED. If not supplied, the most recent entry will be used.",
            dest="date",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            fred_view.display_inflation_indexed_yield_curve(
                date=ns_parser.date.strftime("%Y-%m-%d") if ns_parser.date else "",
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ecbycrv(self, other_args: List[str]):
        """Process ecbycrv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ecbycrv",
            description="Generate euro area yield curve from ECB. \nThe yield curve shows the bond rates"
            "at different maturities.\nThe graphic depiction of the relationship between the yield on bonds of the "
            "same credit quality but different maturities is known as the yield curve. In the past, "
            "most market participants have constructed yield curves from the observations of prices and "
            "yields in the Treasury market. Two reasons account for this tendency. First, "
            "Treasury securities are viewed as free of default risk, and differences in creditworthiness "
            "do not affect yield estimates. Second, as the most active bond market, the Treasury market "
            "offers the fewest problems of illiquidity or infrequent trading. The key function of the "
            "Treasury yield curve is to serve as a benchmark for pricing bonds and setting yields in "
            "other sectors of the debt market.\nIt is clear that the market’s expectations of future rate "
            "changes are one important determinant of the yield-curve shape. For example, "
            "a steeply upward-sloping curve may indicate market expectations of near-term Fed tightening "
            "or of rising inflation. However, it may be too restrictive to assume that the yield "
            "differences across bonds with different maturities only reflect the market’s rate "
            "expectations. The well-known pure expectations hypothesis has such an extreme implication. "
            "The pure expectations hypothesis asserts that all government bonds have the same near-term "
            "expected return (as the nominally riskless short-term bond) because the return-seeking "
            "activity of risk-neutral traders removes all expected return differentials across bonds.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=valid_date,
            help="Date to get data from ECB. If not supplied, the most recent entry will be used.",
            dest="date",
            default=None,
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected type of yield curve",
            default="spot_rate",
            choices=["spot_rate", "instantaneous_forward", "par_yield"],
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            dest="detailed",
            default=False,
            help="If True, returns detailed data. Note that this is very slow.",
        )
        parser.add_argument(
            "--aaa_only",
            action="store_true",
            dest="aaa_only",
            default=True,
            help="If True, it only returns rates for AAA rated bonds. If False, it returns rates for all bonds.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            ecb_view.display_ecb_yield_curve(
                date=ns_parser.date.strftime("%Y-%m-%d") if ns_parser.date else "",
                yield_type=ns_parser.parameter,
                detailed=ns_parser.detailed,
                aaa_only=ns_parser.aaa_only,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )
