import wmi
from ctypes import c_ulong, c_ushort
from core.cfgmgr32 import CM32
from structs.devpropkey import DEVPROPKEY
from structs.guid import GUID
from data.props import props

WMI = wmi.WMI()
cm32 = CM32()


def get_info(pdnDevInst=c_ulong()):
    re_data = {}

    for prop in props:
        try:
            name = prop[0]
            mGUID = GUID(
                Data1=c_ulong(prop[1]),
                Data2=c_ushort(prop[2]),
                Data3=c_ushort(prop[3]),
                Data4=bytes(prop[4]),
            )

            dpkey = DEVPROPKEY(
                fmtid=mGUID,
                pid=c_ulong(prop[5]),
            )

            data = cm32.CM_Get_DevNode_PropertyW(
                pdnDevInst,
                dpkey,
            )

            buff = data.get("data", {}).get("buff")

            if not buff:
                continue

            re_data[name] = buff.raw.decode().replace(" ", "").replace("\x00", "")
        except Exception as e:
            raise e
        
    return re_data


pointing = WMI.instances("Win32_PointingDevice")
kbs = WMI.instances("Win32_Keyboard")

for point in pointing:
    pdnDevInst = c_ulong()
    pnp_id = point.wmi_property("PNPDeviceID").value

    if cm32.CM_Locate_DevNodeA(pdnDevInst, pnp_id.encode("UTF8")).get("code") != 0x0:
        continue

    print(get_info(pdnDevInst))

    parent = c_ulong()

    stat = cm32.CM_Get_Parent(parent, pdnDevInst)

    if stat.get("code", 0x0) != 0x0:
        print(stat)
        continue

    print(get_info(parent))


for kb in kbs:
    pdnDevInst = c_ulong()
    pnp_id = point.wmi_property("PNPDeviceID").value

    if cm32.CM_Locate_DevNodeA(pdnDevInst, pnp_id.encode("UTF8")).get("code") != 0x0:
        continue

    print(get_info(pdnDevInst))

    parent = c_ulong()

    if cm32.CM_Get_Parent(parent, pdnDevInst).get("code", 0x0) != 0x0:
        continue

    print(get_info(parent))
