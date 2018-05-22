'''
########################################################################################################################
# Methods of org.freedesktop.login1.Manager (used or planned for use)
#=======================================================================================================================
# PowerOff(Boolean) -> return None. Example: pm_iface.PowerOff(True)
# Reboot(Boolean) -> return None. Example: pm_iface.Reboot(True)
# Suspend(Boolean) -> return None. Example: pm_iface.Suspend(True)
# Hibernate(Boolean) -> return None. Example  pm_iface.Hibernate(True)
# HybridSleep(Boolean) -> return None. Example: pm_iface.HybridSleep(True)
# CanPowerOff() -> return String. Example: pm_iface.CanPowerOff()
# CanReboot() -> return String. Example: pm_iface.CanReboot()
# CanSuspend() -> return String. Example: pm_iface.CanSuspend()
# CanHibernate() -> return String. Example: pm_iface.CanHibernate()
# CanHybridSleep() -> return String. Example: pm_iface.CanHybridSleep()
# ScheduleShutdown(Str, Int) -> return None. Example: pm_iface.ScheduleShutdown('reboot', now_plus10_min)
#      now_plus10_min = int( datetime.datetime.timestamp(
#             datetime.datetime.now() + datetime.timedelta(minutes=10)
#         ) * 1000000)
# CancelScheduledShutdown() -> return Boolean. Example: pm_iface.CancelScheduledShutdown()
########################################################################################################################
# Properties f org.freedesktop.login1 (used or planned for use)
#=======================================================================================================================
# ScheduledShutdown
#     Example: pm_prop = dbus.Interface(pm, dbus_iface_prop)
#              dobj_prop = pm_prop.Get(dbus_iface, 'ScheduledShutdown')
#              pd_date = datetime.datetime.fromtimestamp(
#                  int(dobj_prop[1] / 1000000)).strftime('%Y-%m-%d %H:%M:%S')
#              sched_sd = str(dobj_prop[0])
########################################################################################################################
# Url on to Docs of D-Bus item login1: https://www.freedesktop.org/wiki/Software/systemd/logind/
########################################################################################################################
'''

__author__ = 'esendjer'
__license__ = 'MIT'
__version__ = '0.1'
__email__ = 'esendjer@gmail.com'
__status__ = 'Development'


import dbus
import datetime
import tkinter as tk
from functools import partial

dbus_item = 'org.freedesktop.login1'                  # This is D-Bus item name for login1
dbus_path = '/org/freedesktop/login1'                 # This is D-Bus item path for login1
dbus_iface = 'org.freedesktop.login1.Manager'         # This is D-Bus item for interface Manager
dbus_iface_prop = 'org.freedesktop.DBus.Properties'   # This is D-Bus item for get properties
dbus_ses_path = '/org/freedesktop/login1/session/self' # This is D-Bus item path for Session
dbus_ses_item = 'org.freedesktop.login1.Session'      # This is D-Bus item name for Session

sysbus = dbus.SystemBus()                     # Create SystemBus object
pm = sysbus.get_object(dbus_item, dbus_path)  # Create object for login1
pm_iface = dbus.Interface(pm, dbus_iface)     # Create interface for login1

pm_prop = dbus.Interface(pm, dbus_iface_prop)             # Create interface for get properties login1
try:
    dobj_prop = pm_prop.Get(dbus_iface, 'ScheduledShutdown')  # Get properties 'ScheduledShutdown' from login1
except:
    dobj_prop='-1'

pm_ses = sysbus.get_object(dbus_item, dbus_ses_path)   # Create object for Session
pm_ses_iface = dbus.Interface(pm_ses, dbus_ses_item)   # Create interface for Session
pm_ses_prop = dbus.Interface(pm_ses, dbus_iface_prop)  # Create interface for get properties Session

id_seesion = pm_ses_prop.Get(dbus_ses_item, 'Id')[0]

if str(dobj_prop[0]) == '':
    sched_sd = 'Нет заплпнированных событий.'
elif dobj_prop == '-1':
    sched_sd = 'Данные о запланированных\nсобытиях не получены.'
else:
    pd_date = datetime.datetime.fromtimestamp(int(dobj_prop[1]/1000000)).strftime('%Y-%m-%d %H:%M:%S')
    sched_sd = 'Заплпнирован {}, на {}.'.format(str(dobj_prop[0]), pd_date)


def get_state(oper_name):
    if oper_name == 'PowerOff':
        return 'disabled' if str(pm_iface.CanPowerOff()) != 'yes' else 'normal'
    elif oper_name == 'Reboot':
        return 'disabled' if str(pm_iface.CanReboot()) != 'yes' else 'normal'
    elif oper_name == 'Suspend':
        return 'disabled' if str(pm_iface.CanSuspend()) != 'yes' else 'normal'
    elif oper_name == 'Hibernate':
        return 'disabled' if str(pm_iface.CanHibernate()) != 'yes' else 'normal'
    elif oper_name == 'HybridSleep':
        return 'disabled' if str(pm_iface.CanHybridSleep()) != 'yes' else 'normal'
    else:
        return 'disabled'


def main():
    wh = 400

    tk_root = tk.Tk()
    tk_root.title('OpenBox PM')
    tk_root.attributes('-zoomed', True)
    tk_root.update_idletasks()
    ws = (tk_root.winfo_width() // 2) - 200
    hs = (tk_root.winfo_height() // 2) - 200
    tk_root.geometry('{}x{}+{}+{}'.format(wh, wh, ws, hs))
    tk_root.attributes('-zoomed', False)
    tk_root.resizable(width=False, height=False)
    tk_root.update_idletasks()

    tk_window = tk.Frame(tk_root)
    tk_window.pack()

    nbtn = partial(tk.Button, tk_window,  height='2', width='30')

    btn_quit = tk.Button(
        tk_window, height='2', width='5', text="QUIT", fg="red", command=tk_root.destroy, state='active'
    )
    btn_quit.pack(side=tk.BOTTOM)

    btn_ses = nbtn(text='Log Out', command=lambda: pm_ses_iface.Terminate())
    btn_ses.pack(side=tk.BOTTOM)
    # pm_iface.TerminateSession(str(id_seesion)) # And it version is wirking

    btn_off = nbtn(text='PowerOff', command=lambda: pm_iface.PowerOff(True), state=get_state('PowerOff'))
    btn_off.pack(side=tk.BOTTOM)

    btn_reb = nbtn(text='Reboot', command=lambda: pm_iface.Reboot(True), state=get_state('Reboot'))
    btn_reb.pack(side=tk.BOTTOM)

    btn_sus = nbtn(text='Suspend', command=lambda: pm_iface.Suspend(True), state=get_state('Suspend'))
    btn_sus.pack(side=tk.BOTTOM)

    btn_hib = nbtn(text='Hibernate', command=lambda: pm_iface.Hibernate(True), state=get_state('Hibernate'))
    btn_hib.pack(side=tk.BOTTOM)

    btn_hsl =  nbtn(text='HybridSleep', command=lambda: pm_iface.HybridSleep(True),state=get_state('HybridSleep'))
    btn_hsl.pack(side=tk.BOTTOM)

    label = tk.Label(tk_window, height='2', text=sched_sd)
    label.pack(side=tk.BOTTOM)

    tk_root.mainloop()


def get_doc():
    for i in __doc__.split('\n'):
        print(i)


if __name__ == '__main__':
    main()