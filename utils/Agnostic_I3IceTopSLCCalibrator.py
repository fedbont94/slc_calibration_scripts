from I3Tray import *
from icecube import icetray, dataclasses, topeventcleaning, icetop_Level3_scripts
from icecube.icetray import I3Module, I3ConditionalModule, I3Frame
from icecube.dataclasses import I3RecoPulseSeriesMapMask, I3EventHeader
from icecube.icetray.i3logging import (
    log_warn,
    log_debug,
)


class Agnostic_I3IceTopSLCCalibrator(I3ConditionalModule):
    """
    This module was adapted from tpx/I3IceTopSLCCalibrator, which was used to calibrate SLC's for L3
    in IC86.2011-2021.
    In that original module, calibration was NOT performed if the chip/atwd-channel number was not known
    (namely, if the IceTopRawData was not present).
    The intent of this module is to "pick up the slack" left behind by that module, and calibrate
    all the other SLC's, by:
    -- Making an educated guess about which ATWD channel it was, based on the charge, and
    -- Averaging the slopes and intercepts from Chip 0 and Chip 1, for that ATWD
    It uses the same "pickle file" used by regular L3 processing.

    This module is to be used on data prior to IC86.2022.  Starting with IC86.2022, the "I3ITSLCCalData"
    frame objects were created and started coming to the north, and there will be a whole different
    (hopefully better) way of calibrating SLC's in the future.  This module is a quick 'n' dirty stopgap
    for the past.
    """

    def __init__(self, ctx):
        I3ConditionalModule.__init__(self, ctx)
        self.AddParameter(
            "SLCPulses",
            "ID of input calibrated SLC pulse list (this gets replaced by default)",
            "IceTopSLCVEMPulses",
        )
        self.AddParameter(
            "SLCPulsesOut",
            "ID of output calibrated SLC pulse list. If it is not specified, it is set equal to SLCPulses. If an object with this name is present, it will be replaced.",
            "",
        )
        self.AddParameter(
            "Config", "Configuration file with the parameters for each OM/chip/ATWD"
        )
        self.AddOutBox("OutBox")

        self.geometry = None
        self.warned = []

    def Configure(self):
        import json  # make python3 happy

        self.slc_name = self.GetParameter("SLCPulses")
        self.slc_name_out = self.GetParameter("SLCPulsesOut")
        if self.slc_name_out == "":
            self.slc_name_out = self.slc_name

        ## The "rb" to read as binary, and the "latin-1" to translate the ASCII
        ## are necessary to make a pickle file from python2 readable by python3.
        ## (This may be able to go away in the future.)
        self.parameters = {}
        with open(self.GetParameter("Config"), "rb") as f:
            for line in f:
                jsonLine = json.loads(line)
                self.createDict_from_json(jsonLine)

    def createDict_from_json(self, line):
        """
        This function takes the json file and creates a dictionary with the parameters for each OM/chip/ATWD
        """
        string = line["value"]["string"]
        om = line["value"]["om"]
        chip = line["value"]["chip"]
        atwd = line["value"]["channel"]
        n = line["value"]["result"]["n"]
        p0 = line["value"]["result"]["p0"]
        p1 = line["value"]["result"]["p1"]
        crossover = line["value"]["result"]["crossover"]
        self.parameters[(string, om, chip, atwd)] = {
            "n": n,
            "p0": p0,
            "p1": p1,
            "crossover": crossover,
        }
        return

    def atwd_educated_guess(self, omkey, charge):
        """
        Gets the crossover value for the OM and compares it to the charge of the pulse.
        ---------------------------------------------
        Parameters:
        omkey: OMKey of the DOM
        charge: charge of the pulse
        ---------------------------------------------
        Returns:
        atwd: Estimated ATWD channel of the pulse
        """
        # TODO The Crossover values are in units of PE, but the charge is in units of VEM!!
        ############ BE CAREFUL!! ##############
        cop01 = (
            self.parameters[(omkey.string, omkey.om, 0, 0)]["crossover"]
            / self.pe_per_vem[omkey]
        )
        cop12 = (
            self.parameters[(omkey.string, omkey.om, 0, 1)]["crossover"]
            / self.pe_per_vem[omkey]
        )
        if charge < cop01:
            atwd = 0
        elif charge < cop12:
            atwd = 1
        else:
            atwd = 2
        return atwd

    def Calibration(self, frame):
        self.pe_per_vem = {}
        I3Cal = frame["I3Calibration"]
        for om in I3Cal.vem_cal.keys():
            self.pe_per_vem[om] = I3Cal.vem_cal[om].pe_per_vem
        self.PushFrame(frame)

    def DAQ(self, frame):
        if not self.slc_name in frame:
            log_debug(
                "I didn't find object %s in the frame.  Moving on." % self.slc_name
            )
            self.PushFrame(frame)
            return

        import copy

        pulses = copy.deepcopy(
            dataclasses.I3RecoPulseSeriesMap.from_frame(frame, self.slc_name)
        )

        # TODO Redo the time check, just in case
        # header = frame["I3EventHeader"]

        # First check whether SLC parameters are defined.
        # We'll use OM 2,61 for this (1 was non-existing in IC79)
        # p = self.parameters[(2, 61, 0, 0)]
        # if (
        #     header.start_time.mod_julian_day_double < p[0][0]
        #     or header.start_time.mod_julian_day_double > p[0][-1]
        # ):
        #     log_fatal(
        #         "Time of this event outside range containing SLC calibration constants."
        #     )

        for om in pulses.keys():
            for i in range(len(pulses[om])):
                # Make an educated guess about the ATWD channel, based on the charge
                atwd = self.atwd_educated_guess(om, pulses[om][i].charge)

                soca = (om.string, om.om, 2, atwd)
                if self.parameters[soca]["n"] > 1:
                    # do the calibration
                    intercept = self.parameters[soca]["p0"]
                    slope = (
                        self.parameters[soca]["p1"] * self.pe_per_vem[om]
                    )  # TODO: This is a hack to convert from PE to VEM
                    # calibrate the pulse!
                    pulses[om][i].charge = intercept + slope * pulses[om][i].charge

                else:
                    log_warn(f"Skipping {om}! (missing SLC calibration information")
                    if not (soca, "calib") in self.warned:
                        self.warned.append((soca, "calib"))

                    # Impossible to calibrate, so set to NaN
                    pulses[om][i].charge = float("nan")

        if self.slc_name_out in frame:
            log_warn(
                "Hey, the output object %s seems to already exist in here.  Will overwrite it.  Are you SURE?"
                % self.slc_name_out
            )
            del frame[self.slc_name_out]
        frame.Put(self.slc_name_out, pulses)
        self.PushFrame(frame)


@icetray.traysegment
def Calibrate_Orphaned_SLCVEMPulses(
    tray,
    name,
    SLCcalibfile="/cvmfs/icecube.opensciencegrid.org/users/icetopusr/SLCcal/slc_calib_parameters_ic86_2012_v1.pcl",  # <- give it the right year!
    SLCVEMPulses="OfflineIceTopSLCVEMPulses",
    SLCTankPulses="OfflineIceTopSLCTankPulses",
):
    """
    "Orphaned" SLCVEMPulses are those for which the IceTopRawData is not present in the frame, and so the Chip/ATWD
    is unknown.  So, at Level3, they are ignored, but left in the frame in the hope that someone would "adopt" them later.
    This tray segment performs a calibration which is "agnostic" to the chip/channel, so it can be performed on any Pulses.
    It follows this with all the other things that are done to calibrated SLC pulses in Level3.
    The output of this module should contain SLC "TankPulses" and look just like the rest of Level3.
    """

    ## ------------ Calibrate the orphans: ---------------
    # These two modules adapted from tpx/segments/CalibrateSLCs:
    # do the calibration
    tray.AddModule(
        Agnostic_I3IceTopSLCCalibrator,
        name
        + "I3IceTopSLCCalibrator",  # <--- replace the normal calibrator (from tpx) with the Agnostic one
        SLCPulses=SLCVEMPulses,
        SLCPulsesOut=SLCVEMPulses + "Calibrated",
        # InputWaveforms = SLCWaveforms,  # nope!
        If=lambda fr: SLCVEMPulses
        in fr,  ## This time, do it only if the VEMPulses are still in there (not the Launches)
        Config=SLCcalibfile,
    )

    # merge into 'tank' pulses
    tray.AddModule(
        "I3TankPulseMerger",
        name + "I3TopTankPulseMerger_SLC",
        InputVEMPulses=SLCVEMPulses + "Calibrated",
        OutputTankPulses=SLCTankPulses,
        ExcludedTanks="TankPulseMergerExcludedSLCTanks",
        If=lambda fr: SLCVEMPulses in fr,  ## Again, change the conditional
    )

    ## ---------- Other things that need to be done to those pulses: -----------------
    ## Time-correct them:
    tray.AddModule(
        icetop_Level3_scripts.modules.I3IceTopSLCTimeCorrect,
        name + "_SLCTimeCorrect",
        SLCPulses=SLCTankPulses,
        If=lambda fr: SLCTankPulses in fr and len(fr[SLCTankPulses]) > 0,
    )

    # Remove the "IceTopSLCVEMPulses" if the calibration was successful
    # tray.AddModule(
    #     "Delete",
    #     name + "_deleteSLCVEMpulses",
    #     Keys=[SLCVEMPulses, SLCVEMPulses + "Calibrated"],
    #     If=lambda fr: SLCTankPulses in fr and len(fr[SLCTankPulses]) > 0,
    # )
