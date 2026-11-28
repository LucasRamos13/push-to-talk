# Push to Talk

Push to talk global para Linux (PipeWire), usando o **Caps Lock** como tecla.
Funciona em Wayland e X11, pois lê o teclado direto via `evdev`.

## Como funciona

- Enquanto um app de voz (**Discord** ou **Stoat**) estiver aberto, todos os
  microfones (`Audio/Source`, incluindo o Easy Effects Source) ficam mutados.
- Segurar **Caps Lock** desmuta; soltar volta a mutar.
- Ao fechar o app de voz (ou parar o script) cada microfone volta ao estado em que estava antes do PTT
  assumir: um mic que já estava mutado continua mutado.
- O mute é reaplicado a cada segundo, caso algo o reverta.
- Teclados conectados/desconectados depois são detectados automaticamente.

## Requisitos

- Python 3 + [`python-evdev`](https://pypi.org/project/evdev/)
- PipeWire + WirePlumber (`pw-dump`, `wpctl`)
- Usuário no grupo `input` (para ler `/dev/input/event*`)
- systemd (serviço de usuário)

## Instalação

```sh
./install.sh
```

Isso:
1. Cria o serviço `~/.config/systemd/user/push-to-talk.service`, que **inicia
   junto com a sessão** e é reiniciado automaticamente se cair.
2. Instala o ícone e o atalho **"Reiniciar Push to Talk"** no menu de aplicativos,
   que finaliza qualquer instância em execução e inicia uma nova
   (clique direito → "Parar Push to Talk" para parar).

Para remover: `./uninstall.sh`.

## Comandos úteis

```sh
systemctl --user status push-to-talk     # status
journalctl --user -u push-to-talk -f     # logs
./restart-ptt.sh                         # reiniciar pelo terminal
```

## Configuração

No topo de `push-to-talk.py`:
- `KEY` — tecla usada (padrão `KEY_CAPSLOCK`)
- `APPS` — apps de voz que ativam o PTT (padrões do `pgrep`)
- `TICK` — intervalo de checagem em segundos
