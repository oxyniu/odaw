from os import system
import sys
import pyinotify

if len(sys.argv) == 1:
    print("Usage: python odaw.py <FILE>")
    sys.exit(1)

def build_ops(func_list):
    ops = 'b main\nr\n'
    for i in func_list:
        ops += 'disas/s ' + i + '\n'
    ops += 'q'
    return ops

def build_command(code):
    ops = build_ops(code.splitlines()[0].split()[1:])
    compile_options = code.splitlines()[1][3:]
    complier = code.splitlines()[2][3:].strip()
    command = 'echo "' + ops + '" >> oda.in && ' + complier + ' ' + compile_options + ' oda.c -o oda && gdb oda < oda.in >> oda.out'
    print(command)
    return command

def da(code: str):
    with open('oda.c', 'w', encoding='utf-8') as file:
        file.write(code)
    system(build_command(code))
    result = ''
    with open('oda.out', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        status = 0
        for line in lines:
            if 'End of assembler dump' in line:
                status = 0
            if status == 1:
                result += line
            if 'Dump of assembler code' in line:
                status = 1
                result += '\n'
    system('rm oda.c oda.in oda oda.out')
    return result

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event=None):
        result = ''
        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            result = da(file.read())
        with open('odaw.out', 'w', encoding='utf-8') as file:
            file.write(result)

handler = MyEventHandler()
handler.process_IN_MODIFY()
wm = pyinotify.WatchManager()
wm.add_watch(sys.argv[1], pyinotify.IN_MODIFY)

notifier = pyinotify.Notifier(wm, handler)
notifier.loop()