#!/usr/bin/env python3
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
#                  int(dobj_prop[1] / 1000000)
#              ).strftime('%Y-%m-%d %H:%M:%S')
#              msg_sched = str(dobj_prop[0])
########################################################################################################################
# Url on to Docs of D-Bus item login1: https://www.freedesktop.org/wiki/Software/systemd/logind/
########################################################################################################################
'''

__author__ = 'esendjer'
__license__ = 'MIT'
__version__ = '0.2'
__email__ = 'esendjer@gmail.com'
__status__ = 'Development'

from typing import Tuple
import dbus
import datetime
import tkinter as tk
from functools import partial
import os


def create_dbus_session() -> Tuple[str, dbus.proxies.Interface, dbus.proxies.Interface, str]:
    dbus_item = 'org.freedesktop.login1'  # This is D-Bus item name for login1
    dbus_path = '/org/freedesktop/login1'  # This is D-Bus item path for login1
    dbus_iface = 'org.freedesktop.login1.Manager'  # This is D-Bus item for interface Manager
    dbus_iface_prop = 'org.freedesktop.DBus.Properties'  # This is D-Bus item for get properties
    dbus_ses_path = '/org/freedesktop/login1/session/self'  # This is D-Bus item path for Session
    dbus_ses_item = 'org.freedesktop.login1.Session'  # This is D-Bus item name for Session

    sysbus = dbus.SystemBus()  # Create SystemBus object
    pm = sysbus.get_object(dbus_item, dbus_path)  # Create object for login1
    pm_iface = dbus.Interface(pm, dbus_iface)  # Create interface for login1

    pm_prop = dbus.Interface(pm, dbus_iface_prop)  # Create interface for get properties login1
    try:
        dobj_prop = pm_prop.Get(dbus_iface, 'ScheduledShutdown')  # Get properties 'ScheduledShutdown' from login1
    except:  # any exceptions
        dobj_prop = '-1'

    pm_ses = sysbus.get_object(dbus_item, dbus_ses_path)  # Create object for Session
    pm_ses_iface = dbus.Interface(pm_ses, dbus_ses_item)  # Create interface for Session
    pm_ses_prop = dbus.Interface(pm_ses, dbus_iface_prop)  # Create interface for get properties Session

    id_seesion = pm_ses_prop.Get(dbus_ses_item, 'Id')[0]

    if str(dobj_prop[0]) == '':
        msg_sched = 'The system has not scheduled tasks.'
    elif dobj_prop == '-1':
        msg_sched = 'The data of scheduled\ntasks was not got.'
    else:
        pd_date = datetime.datetime.fromtimestamp(int(dobj_prop[1] / 1000000)).strftime('%Y-%m-%d %H:%M:%S')
        msg_sched = 'The task {}, was scheduled on {}.'.format(str(dobj_prop[0]), pd_date)
    return id_seesion, pm_ses_iface, pm_iface, msg_sched


def get_state(oper_name):
    state = {
        'Reboot': 'disabled' if str(pm_iface.CanReboot()) != 'yes' else 'normal',
        'Suspend': 'disabled' if str(pm_iface.CanSuspend()) != 'yes' else 'normal',
        'Hibernate': 'disabled' if str(pm_iface.CanHibernate()) != 'yes' else 'normal',
        'HybridSleep': 'disabled' if str(pm_iface.CanHybridSleep()) != 'yes' else 'normal',
        'PowerOff': 'disabled' if str(pm_iface.CanPowerOff()) != 'yes' else 'normal',
        'Log Out': 'normal'
    }
    return state.get(oper_name) or 'disabled'


def cmd(pm_iface: dbus.proxies.Interface, tk_obj: object, act: str, id_seesion: str) -> None:
    if act == 'Log Out':
        # pm_ses_iface.Terminate()             # And this version works
        pm_iface.TerminateSession(id_seesion)  # This version works
    pm_actions = {
        'Reboot': pm_iface.Reboot,
        'Suspend': pm_iface.Suspend,
        'Hibernate': pm_iface.Hibernate,
        'HybridSleep': pm_iface.HybridSleep,
        'PowerOff': pm_iface.PowerOff,
    }
    pm_actions.get(act)(True)
    tk_obj.destroy()


def create_window(id_seesion: str,
                  # pm_ses_iface:dbus.proxies.Interface,
                  pm_iface: dbus.proxies.Interface,
                  msg_sched: str,
                  img_path: str) -> None:
    wh = 350  # The height of window

    # The list of actions
    list_actions = [
        'Log Out',
        'PowerOff',
        'Reboot',
        'Suspend',
        'Hibernate',
        'HybridSleep'
    ]
    dit_images = dict()

    tk_root = tk.Tk()
    tk_root.title('OpenBox PM')

    # images of actions
    icn_quit = tk.PhotoImage(file='{}/icon/application-exit.png'.format(img_path))
    dit_images.update({'Log Out': tk.PhotoImage(file='{}/icon/system-log-out.png'.format(img_path))})
    dit_images.update({'Reboot': tk.PhotoImage(file='{}/icon/gnome-session-reboot.png'.format(img_path))})
    dit_images.update({'Suspend': tk.PhotoImage(file='{}/icon/gnome-session-suspend.png'.format(img_path))})
    dit_images.update({'Hibernate': tk.PhotoImage(file='{}/icon/gnome-session-hibernate.png'.format(img_path))})
    dit_images.update({'HybridSleep': tk.PhotoImage(file='{}/icon/gnome-session-hibernate.png'.format(img_path))})
    dit_images.update({'PowerOff': tk.PhotoImage(file='{}/icon/system-shutdown.png'.format(img_path))})

    tk_root.attributes('-zoomed', True)  # Maximizing the window for detecting resolution of currently active monitor
    tk_root.update_idletasks()  # Updating parameters

    ws = (tk_root.winfo_width() // 2) - 200 + tk_root.winfo_rootx()  # Calculating position the window along the X axis
    hs = (tk_root.winfo_height() // 2) - 245 + tk_root.winfo_rooty()  # Calculating position the window along the Y axis

    tk_root.geometry('{}x490+{}+{}'.format(wh, ws, hs))  # Applying new geometry foe the window
    tk_root.attributes('-zoomed', False)  # Restoring size the window with new geometry
    tk_root.resizable(width=False, height=False)  # Disabling changes size of the window
    tk_root.update_idletasks()  # Updating parameters

    tk_window = tk.Frame(tk_root)
    tk_window.pack()

    # button to exit
    btn_quit = tk.Button(
        tk_window,
        height='38',
        width='100',
        image=icn_quit,
        text='Exit',
        command=tk_root.destroy,
        state='active',
        compound='left'
    )
    btn_quit.focus_set()
    btn_quit.pack(side=tk.BOTTOM, padx=10, pady=15)

    # template for actionable button
    nbtn = partial(tk.Button, tk_window, height='44', width='50', compound='left')

    # create actionable buttons
    for action in list_actions:
        btn = nbtn(
            image=dit_images[action],
            text=action,
            command=lambda x=action: cmd(pm_iface, tk_root, x, id_seesion),
            state=get_state(action)
        )
        btn.pack(side=tk.BOTTOM, padx=5, pady=2, fill='both')

    # create label with info about scheduled tasks
    label = tk.Label(tk_window, height='2', text=msg_sched)
    label.pack(side=tk.BOTTOM, padx=5, pady=2, fill='both')

    tk_root.mainloop()


def get_doc():
    for i in __doc__.split('\n'):
        print(i)


if __name__ == '__main__':
    dir_of_scrip = os.path.dirname(os.path.realpath(__file__))
    id_seesion, _, pm_iface, msg_sched = create_dbus_session()
    create_window(id_seesion, pm_iface, msg_sched, dir_of_scrip)