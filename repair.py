import subprocess
import os
from os import path
import sys
import DESops as d
from lts import StateMachine


class Repair:
    def __init__(self, plant, property, alphabet, controllable, observable):
        self.plant = plant
        self.property = property
        self.controllable = controllable
        self.observable = observable
        self.alphabet = alphabet
    
    def synthesize(self):
        if not path.exists("tmp"):
            os.mkdir("tmp")
        plant = list(map(lambda x: self.lts2fsm(x), self.plant))
        plant = plant[0] if len(plant) == 1 else d.composition.parallel(*plant)
        p = list(map(lambda x: self.lts2fsm(x, extend_alphabet=True), self.property))
        p = p[0] if len(p) == 1 else d.composition.parallel(*p)

        L = d.supervisor.supremal_sublanguage(plant, p, prefix_closed=True, mode=d.supervisor.Mode.CONTROLLABLE_NORMAL)
        L = d.composition.observer(L)
        if len(L.vs) != 0:
            self.fsm2lts(L, "sup")
        else:
            print("Cannot find a controller")

    def lts2fsm(self, file, extend_alphabet=False):
        print("Convert", file, "to fsm model")
        name = path.basename(file)
        tmp_json = f"tmp/{name}.json"
        with open(tmp_json, "w") as f:
            subprocess.run([
                "java",
                "-cp",
                "../bin/robustness-calculator.jar",
                "edu.cmu.isr.robust.ltsa.LTSAHelperKt",
                "--lts",
                file,
            ], stdout=f)
        m = StateMachine.from_json(tmp_json)
        if extend_alphabet:
            m = m.extend_alphabet(self.alphabet)
        tmp_fsm = f"tmp/{name}.fsm"
        m.to_fsm(self.controllable, self.observable, tmp_fsm)
        return d.read_fsm(tmp_fsm)

    def fsm2lts(self, fsm, name):
        fsm_file = f"tmp/{name}.fsm"
        d.write_fsm(fsm_file, fsm)
        m = StateMachine.from_fsm(fsm_file, self.alphabet)
        json_file = f"tmp/{name}.json"
        m.to_json(json_file)
        lts = subprocess.check_output([
            "java",
            "-cp",
            "../bin/robustness-calculator.jar",
            "edu.cmu.isr.robust.ltsa.LTSAHelperKt",
            "--json",
            json_file,
        ], text=True)
        print("=============================")
        print("Synthesized Controller:")
        print(lts)

alphabet = set(["accept_server", "adversary_attacks", "check_info", "encr_device_to_platform", "encr_entity_to_platform", "encr_msg_entity_to_platform", "encr_msg_platform_to_device", "encr_platform_to_device", "encr_platform_to_server", "enter_id_password", "exit", "get_server", "gibberish", "hoax", "msg_device_to_platform", "msg_platform_to_server", "password", "receive_message", "reject", "reject_message", "reject_server", "select_server", "send_message", "server", "server_platform_connect", "success", "verify_message"
])

r = Repair(plant = ["models/protocol/CJ_Tool_protocol_sys.lts", 
                    "models/protocol/CJ_Tool_protocol_env.lts"],
           property = ["models/protocol/CJ_Tool_property_protocol.lts"], 
           alphabet = alphabet,
           controllable =  set(["accept_server", "check_info", "encr_device_to_platform", "encr_entity_to_platform", "encr_msg_entity_to_platform", "encr_msg_platform_to_device", "encr_platform_to_device", "encr_platform_to_server", "enter_id_password", "exit", "get_server", "gibberish", "msg_device_to_platform", "msg_platform_to_server", "receive_message", "reject", "reject_server", "select_server", "send_message", "server", "server_platform_connect", "success"
]),
           observable = alphabet
)

#alphabet = set(["v.enter", "v.exit", "eo.enter", "eo.exit", "v.confirm", 
#               "v.back", "v.vote", "v.select", "v.password", "eo.confirm",
#            "eo.back", "eo.vote", "eo.select", "eo.password"])

#alphabet = set(["v.enter", "v.exit", "eo.enter", "eo.exit", 
 #                "back", "vote", "select", "password", "confirm"])
#r = Repair(plant = ["models/voting/CJ_Tool_Voting_sys.lts",
#               "models/voting/CJ_Tool_voting_sys_env.lts"], 
#        property = ["models/voting/CJ_Tool_property_voting_sys.lts"],
 #       alphabet = alphabet,
#        controllable = set(["v.confirm", "v.back", "v.vote", "v.select", "v.password", "eo.confirm",
#        "eo.back", "eo.vote", "eo.select", "eo.password"]), 
#        controllable = set (["back", "vote", "select", "password", "confirm"]), 
#        observable = alphabet
#)


#alphabet = set(["hPressX", "hPressE", "hPressEnter", "hPressB", "mFire", #"hPressUp", "hPressUp1", "mEBeamLvl", "mXrayLvl",
#        "mInPlace", "mOutPlace", "mInitXray", "mInitEBeam"])
#r = Repair(
#    plant=["models/therac25/interface.lts", "models/therac25/power.lts", #"models/therac25/env.lts"],
#    property=["models/therac25/p.lts"],
#    alphabet=alphabet,
#    controllable=set(["hPressX", "hPressE", "hPressEnter", "hPressB", #"hPressUp", "hPressUp1"]),
#    observable=alphabet
#)

# alphabet = set(["send", "rec", "ack", "getack", "input", "output"])
# r = Repair(
#     plant=["models/abp/channel.lts", "models/abp/receiver.lts", "models/abp/sender.lts"],
#     property=["models/abp/p.lts"],
#     alphabet=alphabet,
#     controllable=alphabet-set(["input", "output"]),
#     observable=alphabet
# )
r.synthesize()
