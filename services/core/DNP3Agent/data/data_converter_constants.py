# Constant definitions for data_converter.py

# Input/Output filenames
POINT_INPUT_FILE = 'mesa_points.xlsx'
POINT_OUTPUT_FILE = 'mesa_points.config'
FUNCTION_INPUT_FILE = 'mesa_functions.xlsx'
FUNCTION_JSON_OUTPUT_FILE = 'mesa_functions.config'
FUNCTION_YAML_OUTPUT_FILE = 'mesa_functions.yaml'

MAX_SCHEDULES = 10
MAX_ARRAY_POINTS = 100

# This script sets all point definitions for a given point type to a particular group and variation.
DATA_TYPES = {'AI': {'group': 30, 'variation': 2},
              'AO': {'group': 40, 'variation': 2},
              'BI': {'group': 1, 'variation': 2},
              'BO': {'group': 10, 'variation': 2}}

# Translate the spreadsheet's function code names to the ones used by this software's point definitions.
FCODE_MAP = {
    'Direct Operate / Response ': 'direct_operate',
    'Direct Operate /Response ': 'direct_operate',
    'Operate / Response ': 'operate',
    ' Operate / Response ': 'operate',
    'Select / Response': 'select',
    ' ': None
}

BAD_POINT_NAMES = ['.', '#REF!', '1.', '7.', '10.']

# Last row number that is read from each of the points worksheets.
LAST_ROW = {
    'AI': 275,
    'AO': 223,
    'BI': 93,
    'BO': 42,
}

# Additional or replacement properties for the point definitions read from the spreadsheet.
# Key is spreadsheet row number.
EXTRA_POINT_DATA = {
    'AI': {
        0: {'index': 443},  # DER version number
        2: {'index': 444},  # DRAT.VRtg
        3: {'index': 445},  # DRAT.WRtg
        6: {'name': 'DCTE.1'},
        31: {'name': 'DOPR.ECPNomHz.1'},
        58: {'name': 'RDGS.DbVMax.1'},
        65: {'name': 'RDGS.HoldTmms.1'},
        93: {'name': 'DCHD.WTgt.1'},
        94: {'name': 'DCHD.WinTms.1'},
        95: {'name': 'DCHD.RmpTms.1'},
        97: {'name': 'DCHD.RmpUpRte.1'},
        98: {'name': 'DCHD.RmpDnRte.1'},
        99: {'name': 'DCHD.ChaRmpUpRte.1'},
        165: {'name': 'DWSM.RmpTms.1'},
        218: {'name': 'DPFC.PFCorRef.rangeC.1'},
        230: {
            'type': 'selector_block',
            'index': 227,
            'selector_block_start': 227,
            'selector_block_end': 442,
        },
        246: {
            'type': 'array',
            'index': 243,
            'name': 'FMAR.in.PairArray.CsvPts',
            'description': 'Curve Points',
            'array_times_repeated': 100,
            'array_points': [
                {'name': 'FMAR.in.PairArray.CsvPts.xVal'},
                {'name': 'FMAR.in.PairArray.CsvPts.yVal'}
            ]
        },
        247: {'operation': 'skip'},
        248: {'operation': 'skip'},
        249: {'operation': 'skip'},
        250: {'operation': 'skip'},
        251: {'operation': 'skip'},
        252: {'operation': 'skip'},
        253: {'operation': 'skip'},
        254: {
            'name': 'FSCC.in.CtlSchdSt.EditSelector',
            'type': 'selector_block',
            'index': 446,
            'selector_block_start': 446,
            'selector_block_end': 655,
        },
        255: {'index': 447, 'name': 'FSCC.in.CtlSchdSt.SelectedSchedulePriority'},
        256: {'index': 448, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleType'},
        257: {'index': 449, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleStartTimeLong1'},
        258: {'index': 450, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleStartTimeLong2'},
        259: {'index': 451, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleRepeatInterval'},
        260: {'index': 452, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleRepeatIntervalUnits'},
        261: {'index': 453, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleValidationStatus'},
        262: {'index': 454, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleStatus'},
        263: {'index': 455, 'name': 'FSCC.in.CtlSchdSt.SelectedScheduleNumberOfPoints'},
        264: {'operation': 'skip'},
        265: {'operation': 'skip'},
        266: {'operation': 'skip'},
        267: {'operation': 'skip'},
        268: {'operation': 'skip'},
        269: {'operation': 'skip'},
        270: {'operation': 'skip'},
        271: {
            'type': 'array',
            'index': 456,
            'name': 'FSCH.in.SchVal',
            'description': 'Schedule Points',
            'array_times_repeated': 100,
            'array_points': [
                {'name': 'FSCH.in.SchVal.val'},
                {'name': 'FSCH.in.SchVal.TimeOffset'}
            ]
        },
        272: {'operation': 'skip'},
        273: {'operation': 'skip'},
        274: {'operation': 'skip'},
        275: {'operation': 'skip'},
    },
    'AO': {
        0: {'index': 404},  # Reference voltage
        2: {'name': 'DRCT.VArRef.1', 'index': 405},
        3: {'name': 'DOPM.WinTms.1', 'index': 406},
        7: {'name': 'DOPM.RvrtTms.1'},
        11: {'name': 'DRCT.RmpUpRte.1'},
        16: {'name': 'DRCC.GridCfgEdt.1'},
        44: {'name': 'DOPM.RvrtTms.2'},
        71: {'name': 'DCHD.RevtTms.1'},
        75: {'name': 'DCHD.ChaRmpDnRte.1'},
        86: {'name': 'DOPM.RvrtTms.3'},
        88: {'name': 'DOPM.RmpTms.1'},
        96: {'name': 'DOPM.RmpTms.2'},
        100: {'name': 'DRCT.WFolRat.1'},
        102: {'name': 'DOPM10.RvrtTms.1'},
        103: {'name': 'DOPM10.RmpTms.1'},
        104: {'name': 'DOPM.RmpTms.3'},
        123: {'name': 'DOPM7.RvrtTms.1'},
        124: {'name': 'DOPM.RmpTms.4'},
        147: {'name': 'DRCT.WMaxLimPct.1'},
        168: {'name': 'DGSM2.1'},
        170: {'name': 'RDGS1.DbVMin.1'},
        188: {'name': 'DOPM1.RmpTms.1'},
        191: {
            'type': 'selector_block',
            'index': 188,
            'selector_block_start': 188,
            'selector_block_end': 403,
        },
        192: {'name': 'DGSMn.ModTyp.1'},
        193: {'name': 'DGSMn.WinTms.1'},
        194: {'name': 'DGSMn.RmpTms.1'},
        195: {'name': 'DGSMn.RvrtTms.1'},
        196: {'name': 'FMARn.PairArray. NumPts.1'},
        197: {'name': 'FMARn.PairArray. MaxPts.1'},
        198: {'name': 'FMARn.IndpUnits.1'},
        199: {'name': 'FMARn.DeptRef.1'},
        200: {'name': 'FMARn.RmpPT1Tms.1'},
        201: {'name': 'FMARn.RmpDecDmm.1'},
        202: {'name': 'FMARn.RmpIncTmm.1'},
        203: {'name': 'FMARn.RmpRsUp.1'},
        204: {'name': 'FMARn.DeptSnptRef.1'},
        205: {'name': 'FMARn.DeptRefStr.1'},
        206: {'name': 'FMAR.out.PairArray.CsvPts.1'},
        207: {
            'type': 'array',
            'index': 204,
            'name': 'FMAR.out.PairArray.CsvPts',
            'description': 'Curve Points',
            'array_times_repeated': 100,
            'array_points': [
                {'name': 'FMAR.out.PairArray.CsvPts.xVal'},
                {'name': 'FMAR.out.PairArray.CsvPts.yVal'}
            ]
        },
        208: {'operation': 'skip'},
        209: {'operation': 'skip'},
        210: {'operation': 'skip'},
        211: {'operation': 'skip'},
        212: {'operation': 'skip'},
        213: {'operation': 'skip'},
        214: {
            'name': 'FSCC.out.CtlSchdSt.EditSelector',
            'type': 'selector_block',
            'index': 407,
            'selector_block_start': 407,
            'selector_block_end': 615,
        },
        215: {'index': 408, 'name': 'FSCC.out.Schd.SelectedScheduleIdentity'},
        216: {'index': 409, 'name': 'FSCC.out.Schd.SelectedSchedulePriority'},
        217: {'index': 410, 'name': 'FSCC.out.Schd.SelectedScheduleType'},
        218: {'index': 411, 'name': 'FSCC.out.Schd.SelectedScheduleStartTimeLong1'},
        219: {'index': 412, 'name': 'FSCC.out.Schd.SelectedScheduleStartTimeLong2'},
        220: {'index': 413, 'name': 'FSCC.out.Schd.SelectedScheduleRepeatInterval'},
        221: {'index': 414, 'name': 'FSCC.out.Schd.SelectedScheduleRepeatIntervalUnits'},
        222: {'index': 415, 'name': 'FSCC.out.Schd.SelectedScheduleNumberOfPoints'},
        223: {
            'type': 'array',
            'index': 416,
            'name': 'FSCH.out.SchVal',
            'description': 'Schedule Points',
            'array_times_repeated': 100,
            'array_points': [
                {'name': 'FSCH.out.SchVal.TimeOffset'},
                {'name': 'FSCH.out.SchVal.val'}
            ]
        },
    },
    'BI': {
        0: {'index': 81},        # System communication error
        1: {'name': 'CALH.GrAlm.1'},
        2: {'name': 'CALH.GrAlm.2', 'index': 82},
        3: {'index': 83},
        25: {'name': 'CSWI. Pos.1'},
        40: {'name': 'DGFL.Beh.1'},
        41: {'name': 'DCHA.Beh.1'},
        56: {'name': 'PTOV.Blk.1'},
        57: {'name': 'PTOV.Str.general.1'},
        58: {'name': 'PTOV.Op.general.1'},
        59: {'name': 'PTUV.Blk.1'},
        60: {'name': 'PTUV.Str.general.1'},
        61: {'name': 'PTUV.Op.general.1'},
        76: {'name': 'DFWS.Mod.1'},
        84: {'index': 84, 'name': 'FSCH.SchdReuse.SelectedScheduleIsReady'},
        85: {'index': 85, 'name': 'FSCH.SchdReuse.SelectedScheduleIsValidated'},
        86: {'index': 86, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklySunday'},
        87: {'index': 87, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklyMonday'},
        88: {'index': 88, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklyTuesday'},
        89: {'index': 89, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklyWednesday'},
        90: {'index': 90, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklyThursday'},
        91: {'index': 91, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklyFriday'},
        92: {'index': 92, 'name': 'FSCH.SchdReuse.SelectedScheduleRepeatWeeklySaturday'},
        93: {'index': 93, 'name': 'FSCH.SchdReuse.OneOrMoreSchedulesRunning'},
    },
    'BO': {
        0: {'index': 32},  # System set lockout state
        2: {'index': 33},  # DRCC.AutoManCtl
        3: {'name': 'DRCC.DERStr.1', 'index': 34},
        7: {'name': 'CSWI. Pos.2'},
        8: {'name': '.EnaCfgDet.1'},
        9: {'name': 'DOPM_x000D_DEXC.OpModIsld_x000D_DrpV.1'},
        11: {'name': 'DRCT.PFExt.1'},
        12: {'name': 'DVRT.Mod.1'},
        14: {'name': 'RDGS.Mod.1'},
        15: {'name': 'DVWD.Mod.1'},
        16: {'name': 'FWHZ.Mod.1'},
        17: {'name': 'DAMG.Mod.1'},
        20: {'name': 'DLFL.Mod.1'},
        21: {'name': 'DGFL.Mod.1'},
        22: {'name': 'DGFL.Mod.2'},
        23: {'name': 'DCHA.Mod.1'},
        24: {'name': 'DWSM.Mod.1'},
        27: {'name': 'DFPF.Mod.1'},
        28: {'name': 'DVVC.Mod.1'},
        29: {'name': 'FPFW.Mod.1'},
        30: {'name': 'DPFC.Mod.1'},
        31: {'name': 'DPRG.Mod.1'},
        32: {'name': 'RDGS.Mod.2'},
        35: {'index': 35, 'name': 'FSCH.SchdReuse.SetSelectedScheduleReady'},
        36: {'index': 36, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklySunday'},
        37: {'index': 37, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklyMonday'},
        38: {'index': 38, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklyTuesday'},
        39: {'index': 39, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklyWednesday'},
        40: {'index': 40, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklyThursday'},
        41: {'index': 41, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklyFriday'},
        42: {'index': 42, 'name': 'FSCH.SchdReuse.SetSelectedScheduleRepeatWeeklySaturday'},
    }
}

EXTRA_FUNCTION_DATA = {
    'disconnect': {
        'ref': 'MESA-ESS spec section 6.2.2 (Table 13)',
        'steps': {
            13: {'action': 'publish'},
        },
    },
    'reconnect': {
        'ref': 'MESA-ESS spec section 6.2.2 (Table 14)',
        'steps': {
            2: {'name': 'DCND.RmpTms.1'},
            4: {'name': 'If switch, CSWI.Pos.1'},
            5: {'action': 'publish'},
        },
    },
    'cease_to_energize': {
        'ref': 'MESA-ESS spec section 6.2.3 (Table 15)',
        'steps': {
            2: {'name': 'DCTE.RmpTms.1'},
            4: {'action': 'publish'},
        },
    },
    'return_to_service': {
        'ref': 'MESA-ESS spec section 6.2.3 (Table 16)',
        'steps': {
            4: {'action': 'publish'},
        },
    },
    'low_high_voltage_ride_through': {
        'ref': 'MESA-ESS spec section 6.3.1 (Table 17)',
        'support_point': 'DVRT.Beh',
        'steps': {
            36: {'action': 'publish'},
        },
    },
    'low_high_freq_ride_through': {
        'ref': 'MESA-ESS spec section 6.3.2 (Table 18)',
        'support_point': 'DFRT.Beh',
        'steps': {
            8: {'action': 'publish'},
        },
    },
    'dynamic_reactive_current': {
        'ref': 'MESA-ESS spec section 6.3.3.6 (Table 20)',
        'support_point': 'RDGS.Beh',
        'steps': {
            13: {'action': 'publish'},
        },
    },
    'dynamic_volt_watt': {
        'ref': 'MESA-ESS spec section 6.3.4 (Table 21)',
        'support_point': 'DVWD.Beh',
        'steps': {
            10: {'action': 'publish'},
        },
    },
    'frequency_watt_emergency': {
        'ref': 'MESA-ESS spec section 6.3.5 (Table 22)',
        'support_point': 'FWHZ.Beh',
        'steps': {
            14: {'action': 'publish'},
        },
    },
    'charge_discharge': {
        'ref': 'MESA-ESS spec section 6.4.1 (Table 23)',
        'support_point': 'DCHA.Beh',
        'steps': {
            11: {'action': 'publish'},
        },
    },
    'coordinated_charge_discharge': {
        'ref': 'MESA-ESS spec section 6.4.2 (Table 24)',
        'support_point': 'DCBY.Beh',
        'steps': {
            18: {'action': 'publish'},
        },
    },
    'active_power_limit': {
        'ref': 'MESA-ESS spec section 6.4.3 (Table 25)',
        'support_point': 'DAMG.Beh',
        'steps': {
            9: {'action': 'publish'},
        },
    },
    'peak_power_limiting': {
        'ref': 'MESA-ESS spec section 6.4.4 (Table 26)',
        'support_point': 'DLFL.Beh',
        'steps': {
            11: {'action': 'publish'},
        },
    },
    'load_following': {
        'ref': 'MESA-ESS spec section 6.4.5 (Table 27)',
        'support_point': 'DGFL.Beh',
        'steps': {
            11: {'action': 'publish'},
        },
    },
    'generation_following': {
        'ref': 'MESA-ESS spec section 6.4.6 (Table 28)',
        'support_point': 'DGFL.Beh.1',
        'steps': {
            13: {'action': 'publish'},
        },
    },
    'automatic_generation_control': {
        'ref': 'MESA-ESS spec section 6.4.7 (Table 29)',
        'support_point': 'DCHA.Beh.1',
        'steps': {
            10: {'action': 'publish'},
            12: {'name': 'DRCT.MaxRmpUpRte.1'},
            13: {'name': 'DRCT.MaxRmpDnRte.1'},
        },
    },
    'active_power_smoothing': {
        'ref': 'MESA-ESS spec section 6.4.8 (Table 30)',
        'support_point': 'DWSM.Beh',
        'steps': {
            15: {'action': 'publish'},
        },
    },
    'volt_watt': {
        'ref': 'MESA-ESS spec section 6.4.9 (Table 31)',
        'support_point': 'DVWA_x000D_DVVM.Beh',
        'steps': {
            16: {'action': 'publish'},
        },
    },
    'frequency_watt_curve': {
        'ref': 'MESA-ESS spec section 6.4.10.3 (Table 32)',
        'support_point': 'DFWS.Beh',
        'steps': {
            3: {'name': 'DOPR.ECPNomHz.1'},
            8: {'action': 'publish'},
        },
    },
    'fixed_power_factor': {
        'ref': 'MESA-ESS spec section 6.5.1 (Table 33)',
        'support_point': 'DFPF.Beh',
        'steps': {
            7: {'action': 'publish'},
        },
    },
    'volt_var_control': {
        'ref': 'MESA-ESS spec section 6.5.2 (Table 34)',
        'support_point': 'DVVC.Beh',
        'steps': {
            7: {'action': 'publish'},
        },
    },
    'watt_var': {
        'ref': 'MESA-ESS spec section 6.5.3 (Table 35)',
        'support_point': 'FPFW.Beh',
        'steps': {
            7: {'action': 'publish'},
        },
    },
    'power_factor_limiting': {
        'ref': 'MESA-ESS spec section 6.5.4 (Table 36)',
        'support_point': 'DPFC.Beh',
        'steps': {
            7: {'name': 'DPFC.PFRef.rangeC.1'},
            9: {'action': 'publish'},
        },
    },
    'schedule_creation': {
        'ref': 'MESA-ESS spec section 6.6 (Table 37)',
        'steps': {
            6: {'action': 'publish'},
        },
    },
    'schedule_enable': {
        'ref': 'MESA-ESS spec section 6.6 (Table 38)',
        'steps': {
            5: {'action': 'publish'},
            7: {'name': 'FSCHxx.SchdReuse1'},
            8: {'name': 'FSCHxx.SchdReuse2'},
            9: {'name': 'FSCHxx.SchdReuse3'},
            10: {'name': 'FSCHxx.SchdReuse4'},
            11: {'name': 'FSCHxx.SchdReuse5'},
            12: {'name': 'FSCHxx.SchdReuse6'},
            13: {'name': 'FSCHxx.SchdReuse7'},
        },
    },
    'curve': {
        'ref': 'Not documented explicitly in the MESA-ESS spec',
        'steps': {
            13: {'action': 'publish'},
        },
    },
    'Schedule': {
        'ref': 'Not documented explicitly in the MESA-ESS spec',
        'steps': {
            3: {'action': 'publish'},
        },
    },
}

# Many function steps reference names of analog output points that aren't defined in the spreadsheet.
# Add definitions for those points.
MORE_POINTS = {
    'AO': [
        "DCND.WinTms",
        "DCND.RmpTms",
        "DCND.RmpTms.1",
        "DCND.RvrtTms",
        "If switch, CSWI.Pos",
        "If not switch, DCND.DERStop",
        "DCND.StrWinTms",
        "DCND.ECPStrAuth",
        "If not switch, DCND.DERStr",
        "DCTE.RmpTms",
        "DCTE.RmpTms.1",
        "DCTE.StrWinTms",
        "DCTE.ECPClsAuth",
        "DCTE.DERStr",
        "DVRT.ECPRefId",
        "DVRT.VolRef",
        "DRCT.VRegOfs",
        "DVRT.CurveVHiTr",
        "DVRT.CurveVHiCea",
        "DVRT.CurveVLoCea",
        "DVRT.CurveVLoTr",
        "DVRT.ModEna",
        "DVRT.ModVRtSt",
        "DFRT.ECPRef",
        "DFRT.HzRef",
        "DFRT.NomHz",
        "DFRT.CurveHzHiTr",
        "DFRT.CurveHzHiCea",
        "DFRT.CurveHzLoCea",
        "DFRT.CurveHzLoTr",
        "DFRT.ModHzRtSt",
        "DFRT.ModEna",
        "RDGS.ECPRefId",
        "RDGS.ArGraSwl",
        "RDGS.FilTms",
        "RDGS.ModPrity",
        "RDGS.ModEna",
        "RDGS.EvtEna (not in IEC 61850 yet)",
        "RDGS.VArMaxAvl (not in IEC 61850 yet)",
        "RDGS.VAv",
        "DVWD.ECPRefId",
        "DVWD.DynVWGra",
        "DVWD.VWFilTms",
        "DVWD.DbVWLo",
        "DVWD.DbVWHi",
        "DVWD.RevtTms",
        "DVWD.ModEna",
        "DVWD.ModPrty",
        "DVWD.DelV",
        "DVWD.VAv",
        "FWHZ.ECPRefId",
        "FWHZ.HzRef",
        "FWHZ.WinTms",
        "FWHZ.RmpTms",
        "FWHZ.RvrtTms",
        "FWHZ.HzStr",
        "FWHZ.HzStop",
        "FWHZ.HzStopWGra",
        "FWHZ.ActDlTmms",
        "FWHZ.HysEna",
        "FWHZ.SnptW",
        "FWHZ.ModPrty",
        "FWHZ.WCtlHzEna",
        "DCHD.RvrtTms",
        "DCHD.ModEna",
        "DTCD.RvrtTms",
        "DTCD.Tms.Tgt",
        "DTCD.ModEna",
        "DRCT.MaxRmpUpRte",
        "DRCT.MaxRmpDnRte",
        "DAMG.ECPRefId",
        "DAMG.ModEna",
        "DPKP.ECPRefId",
        "DPKP.WRef",
        "DPKP.RvrtTms",
        "DPKP.ModEna",
        "DLFL.ECPRefId",
        "DLFL.RvrtTms",
        "DLFL.ModEna",
        "DGFL.ECPRefId",
        "DGFL.RvrtTms",
        "DGFL.ModEna",
        "DAGC.WinTms",
        "DAGC.RmpTms",
        "DAGC.RvrtTms",
        "DAGC.ModEna",
        "DWSM.ECPRefId",
        "DWSM.RvrtTms",
        "DWSM.RmpUpRte",
        "DWSM.RmpDnRte",
        "DWSM.ChaRmpUpRte",
        "DWSM.ChaRmpDnRte",
        "DWSM.ModEna",
        "DVWG.ECPRefId",
        "DVWG.WRef",
        "DVWG.RmpTms",
        "DVWG.RvrtTms",
        "DVWG.ModEna",
        "DFWS.ECPRefId",
        "DFWS.HzRef",
        "DFWS.PairArrHzW",
        "DFWS.WinTms",
        "DFWS.RmpTms",
        "DFWS.RvrtTms",
        "DFPF.ECPRefId",
        "DFPF.RvrtTms",
        "DFPF.ModEna",
        "DVVC.ECPRefId",
        "DVVC.RvrtTms",
        "DVVC.PairArrVVar",
        "DVVC.ModEna",
        "DWVR.ECPRefId",
        "DWVR.VRef",
        "DWVR.WinTms",
        "DWVR.RmpTms",
        "DWVR.RvrtTms",
        "DWVR.PairArrVVar",
        "DWVR.ModEna",
        "DWVR.ModPrty",
        "DPFC.ECPRefId",
        "DPFC.PFRef",
        "DPFC.RmpTms",
        "DPFC.RvrtTms",
        "DPFC.PFRef.rangeC",
        "DPFC.ModEna",
        "FSCHxx (the xx refers to the schedule number (index)",
        "FSCHxx.ValASG (with FSCH.ClcIntvTyp set to seconds)",
        "FSCHxx.ValASG (set for power system values and pricing signals)",
        "FSCHxx.ING (set to the operational mode identity)",
        "FSCHxx.RmpTms",
        "FSCHxx.NumEntr",
        "FSCHxx.SchdPrio",
        "FSCHxx.ValMV (for power system values or pricing signals) or FSCH.ValINS (for operational modes) (meanings of pricing signals need to be defined)",
        "FSCC.Schd",
        "FSCHxx.StrTm",
        "FSCHxx.IntvPer",
        "FSCHxx.ClcIntvTyp",
        "FSCHxx.Enable",
        "FSCH.SchdSt.2",
        "FSCHxx.SchdReuse1",
        "FSCHxx.SchdReuse2",
        "FSCHxx.SchdReuse3",
        "FSCHxx.SchdReuse4",
        "FSCHxx.SchdReuse5",
        "FSCHxx.SchdReuse6",
        "FSCHxx.SchdReuse7",
        "FSCC.ActSchdRef",
        "DOPR.ECPNomHz",
        "DPFC.PFRef.rangeC.1",
        "DRCT.MaxRmpUpRte.1",
        "DRCT.MaxRmpDnRte.1",
        "If switch, CSWI.Pos.1",
    ]
}

CURVE_FUNCTION_POINTS = {
    'edit_selector_name': 'Curve Edit Selector',
    'other_point_names': [
        'Curve Mode Type',
        'Curve Time Window',
        'Curve Ramp Time',
        'Curve Revert Time',
        'Curve Number of Points',
        'Curve Maximum Number of Points',
        'Independent (X-Value) Units for Curve',
        'Dependent (Y-Value) Units for Curve',
        'Curve Time Constant',
        'Curve Decreasing Max Ramp Rate',
        'Curve Increasing Ramp Rate',
    ],
    'array_point_name': 'CurveStart',
    'array_columns': [{'name': 'CurveX'}, {'name': 'CurveY'}],
}

SCHEDULE_FUNCTION_POINTS = {
    'edit_selector_name': 'Schedule Edit Selector',
    'other_point_names': [
        'Schedule Enable',
    ],
    'array_point_name': 'Schedule Start',
    'array_columns': [{'name': 'Schedule Time'}, {'name': 'Schedule Value'}],
}

SCHEDULE_FUNCTION = {
    'name': 'Schedule',
    'steps': [
        {
            'Step ': 1,
            'IEC 61850 ': 'Schedule Edit Selector',
            'Description ': '',
            'M/O/C ': 'M',
        },
        {
            'Step ': 2,
            'IEC 61850 ': 'Schedule Start',
            'Description ': '',
            'M/O/C ': 'M',
        },
        {
            'Step ': 3,
            'IEC 61850 ': 'Schedule Enable',
            'Description ': '',
            'M/O/C ': 'M',
        },
    ]
}


def extra_data_for_function(function_name, data_element_name):
    """Return extra data for the indicated function and data element, or None."""
    return EXTRA_FUNCTION_DATA.get(function_name, {}).get(data_element_name, None)


def extra_data_for_function_step(function_name, step_number, data_element_name):
    """Return extra data for the indicated function step and data element, or None."""
    func_data = extra_data_for_function(function_name, 'steps')
    return func_data.get(step_number, {}).get(data_element_name, None) if func_data else None


def extra_point_data(data_type_name, row_num):
    """Return extra data for the indicated data type, spreadsheet row number and data element, or None."""
    return EXTRA_POINT_DATA.get(data_type_name, {}).get(row_num, {})
