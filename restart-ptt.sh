#!/bin/sh
# Finaliza qualquer instância do push-to-talk e inicia uma nova via systemd.
systemctl --user stop push-to-talk.service 2>/dev/null
pkill -f 'push-to-talk\.py' 2>/dev/null   # instâncias abertas manualmente
sleep 0.5
pkill -9 -f 'push-to-talk\.py' 2>/dev/null
systemctl --user reset-failed push-to-talk.service 2>/dev/null
if systemctl --user start push-to-talk.service && sleep 1 && systemctl --user is-active -q push-to-talk.service; then
    notify-send -a "Push to Talk" -i push-to-talk "Push to Talk" "Reiniciado com sucesso" 2>/dev/null
else
    notify-send -a "Push to Talk" -i dialog-error -u critical "Push to Talk" "Falha ao iniciar — veja: journalctl --user -u push-to-talk" 2>/dev/null
fi
