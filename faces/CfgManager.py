import configparser
import os


def change_cfg():
    curpath = os.path.dirname(os.path.realpath(__file__))
    cfgpath = os.path.join(curpath, "Config/cfg.ini")
    conf = configparser.ConfigParser()
    conf.read(cfgpath, encoding="utf-8")
    print('\033[1;33m===============Settings===============\033[0m')
    sections = conf.sections()
    section_num = 1
    for section in sections:
        print('%d.%s' % (section_num, section))
        section_num += 1
    # 选择Section
    flag1 = False
    while flag1 is False:
        key = int(
            input('\033[4;33mwhat kind of setting would you like to change? (enter num then press enter): \033[0m'))
        if 0 < key <= len(sections):
            selected_section = sections[key - 1]
            flag1 = True
            print('\033[1;32m>>>%s\033[0m' % selected_section)
        else:
            print('\033[1;31mPlease enter a number representing the function!\033[0m')

    items = conf.items(str(selected_section))
    item_num = 1
    for item in items:
        print('   %d.%s' % (item_num, item[0]))
        item_num += 1
    # 选择Item
    flag2 = False
    while flag2 is False:
        key = int(input('\033[4;33mwhich setting would you like to change? (enter num then press enter): \033[0m'))
        if 0 < key <= len(items):
            selected_item = items[key - 1][0]
            flag2 = True
            print("\033[1;30;41m%s\033[0m now is \033[1;30;42m'%s'\033[0m" % (selected_item, items[key - 1][1]))
            new_key = input('\033[4;33mplease enter the changed value: \033[0m')
            ask = input(
                "are you sure change \033[1;30;41m%s\033[0m to \033[1;30;42m'%s'\033[0m(enter 'y' to continue): " % (selected_item, new_key))
            if ask == 'y':
                conf.set(selected_section, selected_item, new_key)
                conf.write(open(cfgpath, "w"))
        else:
            print('\033[1;31mPlease enter a number representing the function!\033[0m')


def read_cfg(setting_name):
    curpath = os.path.dirname(os.path.realpath(__file__))
    cfgpath = os.path.join(curpath, "Config/cfg.ini")
    conf = configparser.ConfigParser()
    conf.read(cfgpath, encoding="utf-8")
    sections = conf.sections()
    for section in sections:
        items = conf.items(section)
        for item in items:
            if item[0] == setting_name:
                return item[1]


def show_cfgtree():
    curpath = os.path.dirname(os.path.realpath(__file__))
    cfgpath = os.path.join(curpath, "Config/cfg.ini")
    conf = configparser.ConfigParser()
    conf.read(cfgpath, encoding="utf-8")
    sections = conf.sections()
    for section in sections:
        items = conf.items(section)
        print('├── %s' % section)
        for item in items:
            print('│   ├── %s' % item[0], end='')
            print('    [%s]' % item[1])
