import glob
import json
import numpy as np

from icecube import icetray, dataio, vemcal

from utils.crossover_points import calculate_crossOverPoints
from utils.calculate_p0_p1 import calculate_p0_p1


def read_calibrationFromRuns(slc_hlc_q_dict, slc_hlc_sum_q_dict, files_list, r):
    slcdata_name = "I3ITSLCCalData"

    for f in sorted(files_list):
        print(f"Reading file {f}")
        for frame in dataio.I3File(f):
            # Is this one of the streams you wanted (Q or P)?
            if frame.Stop not in [icetray.I3Frame.Physics]:
                continue
            # IF there is no slc calibration information, skip
            if slcdata_name not in frame:
                continue

            slcdata = frame[slcdata_name]

            if frame.Has(
                "I3EventHeader"
            ):  # At Lv2, all frames have an I3EventHeader, but this is not true for PFFilt
                header = frame["I3EventHeader"]

                # if start is None:
                #     start = header.start_time
                #     end = header.end_time
                # if end < header.end_time:
                #     end = header.end_time

            ## Run number sanity checks
            if not header.run_id == r:
                SystemExit("I3EventHeader and I3ITSLCCalItem run numbers do not match!")

            itemlist = slcdata.HLC_vs_SLC_Hits

            for calkey in itemlist:
                # It's just a vector of Items; Each "calkey" is a ITSCLCalItem
                ## Each "calkey" is a custom lightweight object... extract the info!
                omkey = icetray.OMKey(calkey.string, calkey.om)
                chip = calkey.chip
                atwd = calkey.atwd

                ## What is stored is "deci-photoelectrons"
                hlcc = calkey.hlc_charge_dpe / 10.0
                slcc = calkey.slc_charge_dpe / 10.0

                # Add the calibration to the collection
                slc_hlc_q_dict[omkey][f"atwd{atwd}"] = np.append(
                    slc_hlc_q_dict[omkey][f"atwd{atwd}"], [[slcc], [hlcc]], axis=1
                )

                # Add the calibration to the sum collection for the p0 p1 fit
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["n"] += 1
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["x"] += slcc
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["xx"] += slcc**2
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["y"] += hlcc
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["yy"] += hlcc**2
                slc_hlc_sum_q_dict[omkey][f"chip{chip}atwd{atwd}"]["xy"] += slcc * hlcc

        print(f"Completed file {f}")
    return


def tuple_to_str(key):
    return ",".join(str(i) for i in key)


def str_to_tuple(key_str):
    return tuple(key_str.split(","))


def main():
    r = 138329
    yr = 2023

    files_list = sorted(
        glob.glob(
            f"/data/exp/IceCube/{yr}/filtered/PFFilt/090[67]/PFFilt_PhysicsFiltering_Run00{r}_Subrun00000000_00000000*.tar.bz2"
        )
    )

    # Create a dictionary of OMKeys
    # with empty arrays for each ATWD
    # array shape: (2, 0)
    # 1. array slc calibration
    # 2. array hlc calibration
    slc_hlc_q_dict = {}
    slc_hlc_sum_q_dict = {}

    for string in range(1, 82):
        for om in range(61, 65):
            omkey = icetray.OMKey(string, om)
            slc_hlc_q_dict[omkey] = {
                "atwd0": np.array([[], []]),
                "atwd1": np.array([[], []]),
                "atwd2": np.array([[], []]),
            }
            chipATWDkeys = [
                "chip0atwd0",
                "chip0atwd1",
                "chip0atwd2",
                "chip1atwd0",
                "chip1atwd1",
                "chip1atwd2",
            ]
            slc_hlc_sum_q_dict[omkey] = {
                cakey: {
                    "n": 0,
                    "x": 0.0,
                    "xx": 0.0,
                    "y": 0.0,
                    "yy": 0.0,
                    "xy": 0.0,
                }
                for cakey in chipATWDkeys
            }

            # "run": r,
            # "start_time": start_time,
            # "end_time": end_time,
    read_calibrationFromRuns(slc_hlc_q_dict, slc_hlc_sum_q_dict, files_list, r)

    # p0_p1_dict = calculate_p0_p1(slc_hlc_sum_q_dict)

    crossOvers_dict = calculate_crossOverPoints(slc_hlc_q_dict, bad_doms_list=[])

    save_dict_charges = {
        tuple_to_str(key): value for key, value in slc_hlc_sum_q_dict.items()
    }
    save_dict_crossOvers = {
        tuple_to_str(key): value for key, value in crossOvers_dict.items()
    }

    with open("/data/user/fbontempo/test/chargeSums_dict.json", "w") as f:
        json.dump(save_dict_charges, f)
    with open("/data/user/fbontempo/test/crossOvers_dict.json", "w") as f:
        json.dump(save_dict_crossOvers, f)
    return


if __name__ == "__main__":
    main()
    print("-------------------- Program finished --------------------")
