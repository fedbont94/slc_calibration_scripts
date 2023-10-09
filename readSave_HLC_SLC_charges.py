import glob
import pickle
import numpy as np
import multiprocessing as mp
from icecube import icetray, dataio, vemcal


def read_calibrationFromRuns(slccal_dict, files_list, r):
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
            ):  # At L2, all frames have an I3EventHeader, but this is not true for PFFilt
                header = frame["I3EventHeader"]
                run_id = header.run_id
                run_time = header.start_time

                ## Run number sanity checks
                if not header.run_id == r:
                    exit("I3EventHeader and I3ITSLCCalItem run numbers do not match!")

            itemlist = slcdata.HLC_vs_SLC_Hits

            for calkey in itemlist:
                # It's just a vector of Items; Each "calkey" is a ITSCLCalItem
                ## Each "calkey" is a custom lightweight object... extract the info!
                key = icetray.OMKey(calkey.string, calkey.om)
                chip = calkey.chip
                atwd = calkey.atwd

                ## What is stored is "deci-photoelectrons"
                hlcc = calkey.hlc_charge_dpe / 10.0
                slcc = calkey.slc_charge_dpe / 10.0

                # Add the calibration to the collection
                slccal_dict[key][f"atwd{atwd}"] = np.append(
                    slccal_dict[key][f"atwd{atwd}"], [[slcc], [hlcc]], axis=1
                )
        print(f"Completed file {f}")
    return


def main():
    r = 138329
    yr = 2023

    files_list = sorted(
        glob.glob(
            f"/data/exp/IceCube/{yr}/filtered/PFFilt/090[67]/PFFilt_PhysicsFiltering_Run00{r}_Subrun00000000_000000*.tar.bz2"
        )
    )

    # Create a dictionary of OMKeys
    # with empty arrays for each ATWD
    # array shape: (2, 0)
    # 1. array slc calibration
    # 2. array hlc calibration
    slccal_dict = {}
    for string in range(1, 82):
        for om in range(61, 65):
            key = icetray.OMKey(string, om)
            slccal_dict[key] = {
                "atwd0": np.array([[], []]),
                "atwd1": np.array([[], []]),
                "atwd2": np.array([[], []]),
            }

    # for each file in file list spawn a process
    # to read the calibration information
    # from the slcdata
    # processes = []
    # for f in files_list:
    #     p = mp.Process(target=read_calibrationFromRuns, args=(slccal_dict, [f], r))
    #     p.start()
    #     processes.append(p)

    # for p in processes:
    # p.join()

    read_calibrationFromRuns(slccal_dict, files_list, r)

    with open("/data/user/fbontempo/test/SLCCal_test.pkl", "wb") as f:
        pickle.dump(slccal_dict, f)
    return


if __name__ == "__main__":
    main()
    print("-------------------- Program finished --------------------")
