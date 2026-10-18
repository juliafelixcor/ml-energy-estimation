import ctypes
import sys

# Lê o estado da bateria pela API nativa do Windows (CallNtPowerInformation).
# Com o notebook FORA DA TOMADA, a taxa de descarga corresponde à potência
# consumida pelo sistema inteiro — é uma medição real, não uma estimativa.
# A chamada custa ~0,1 ms, então não interfere no consumo medido.
# O Windows atualiza esse valor a cada ~5-20 s, por isso cada janela de
# medição precisa durar pelo menos ~1 minuto.


class _SystemBatteryState(ctypes.Structure):
    _fields_ = [
        ("AcOnLine", ctypes.c_ubyte),
        ("BatteryPresent", ctypes.c_ubyte),
        ("Charging", ctypes.c_ubyte),
        ("Discharging", ctypes.c_ubyte),
        ("Spare1", ctypes.c_ubyte * 3),
        ("Tag", ctypes.c_ubyte),
        ("MaxCapacity", ctypes.c_uint32),        # mWh
        ("RemainingCapacity", ctypes.c_uint32),  # mWh
        ("Rate", ctypes.c_int32),                # mW
        ("EstimatedTime", ctypes.c_uint32),
        ("DefaultAlert1", ctypes.c_uint32),
        ("DefaultAlert2", ctypes.c_uint32),
    ]


_SYSTEM_BATTERY_STATE = 5


class BatterySensor:
    name = "battery"

    def __init__(self):
        self.available = False

        if sys.platform != "win32":
            return

        try:
            self._call = ctypes.windll.powrprof.CallNtPowerInformation
            self.available = bool(self._query().BatteryPresent)
        except Exception:
            self.available = False

    def _query(self):
        state = _SystemBatteryState()
        self._call(_SYSTEM_BATTERY_STATE, None, 0, ctypes.byref(state), ctypes.sizeof(state))
        return state

    def read(self):
        state = self._query()
        discharging = bool(state.Discharging) and not state.AcOnLine

        return {
            "on_battery": discharging,
            # O sinal de Rate varia entre fabricantes; só vale como consumo quando está descarregando
            "battery_power_W": abs(state.Rate) / 1000.0 if discharging else float("nan"),
            "battery_remaining_mWh": state.RemainingCapacity,
            "battery_%": 100.0 * state.RemainingCapacity / state.MaxCapacity if state.MaxCapacity else float("nan"),
        }
