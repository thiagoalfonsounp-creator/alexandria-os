import os,pty,fcntl,termios,struct,select,time,signal,sys
from pathlib import Path
import pyte
root=str(Path(__file__).resolve().parents[1])
def check(cols,rows):
 pid,fd=pty.fork()
 if pid==0:
  fcntl.ioctl(0,termios.TIOCSWINSZ,struct.pack('HHHH',rows,cols,0,0))
  os.chdir(root)
  os.environ.update(TERM='xterm-256color',ESCDELAY='25',LANG='C.UTF-8',XDG_STATE_HOME='/tmp/alexandria-smoke-state')
  os.execv('/bin/bash',['bash','bin/alexandria'])
 screen=pyte.Screen(cols,rows); stream=pyte.Stream(screen); rawlog=bytearray()
 def read():
  until=time.monotonic()+0.6
  while time.monotonic()<until:
   if select.select([fd],[],[],0.05)[0]:
    try:b=os.read(fd,65536)
    except OSError:break
    if not b:break
    rawlog.extend(b);stream.feed(b.decode('utf-8','replace'))
  return '\n'.join(screen.display)
 try:
  text=read();open(f'/tmp/alexandria-menu-{cols}x{rows}.txt','w').write(text);open(f'/tmp/alexandria-menu-{cols}x{rows}.raw','wb').write(rawlog)
  assert all(t in text for t in ('ALEXANDRIA OS 0.6','THE WORLD','THE COMIC ARCHIVE','THE REFUGE','CUADERNO DE CAMPO','MANUAL / AYUDA','TERMINAL')),text
  assert 'TWD' not in text
  world_y=next(i for i,line in enumerate(screen.display) if 'THE WORLD' in line)
  assert screen.display[world_y].index('THE WORLD') >= cols // 2
  logo_cells=[cell for y,row in screen.buffer.items() for x,cell in row.items()
              if x < cols // 2 and (cell.fg not in ('default','white') or cell.bg not in ('default','black'))]
  assert len(logo_cells)>100,f'La imagen no se representó en el panel izquierdo: {len(logo_cells)} celdas'
  red_cells=[cell for cell in logo_cells if str(cell.fg).lower() in ('800000','af0000','d70000','ff0000','red')
             or str(cell.bg).lower() in ('800000','af0000','d70000','ff0000','red')]
  assert len(red_cells)>20,f'No se encontró el rojo del logo: {len(red_cells)} celdas'
  os.write(fd,b'5\n');text=read();assert 'MANUAL / AYUDA' in text,text
  os.write(fd,b'\x1b');read()
  os.write(fd,b'1\n');text=read();assert 'Personajes' in text and 'Comunidades' in text,text
  os.write(fd,b'\x1b');read()
  os.write(fd,b'3\n');text=read();assert 'THE REFUGE' in text and ('partida' in text.lower() or 'Continuar' in text),text
  os.write(fd,b'\x1b');read()
  os.write(fd,b'6\n');read()
  got,status=os.waitpid(pid,os.WNOHANG);assert got==pid and os.waitstatus_to_exitcode(status)==0
  print(f'PASS {cols}x{rows}: imagen en panel izquierdo, menú legible a la derecha, seis opciones, ayuda, THE WORLD, apertura de THE REFUGE y salida (0)')
 finally:
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
  os.close(fd)
for size in [(80,24),(120,40)]:check(*size)
