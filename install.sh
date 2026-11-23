#!/bin/sh
# Instala o Push to Talk: serviço systemd (inicia com o sistema), ícone e atalho no menu.
set -e
D="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.config/systemd/user ~/.local/share/icons/hicolor/scalable/apps ~/.local/share/applications
chmod +x "$D/push-to-talk.py" "$D/restart-ptt.sh"

cat > ~/.config/systemd/user/push-to-talk.service <<UNIT
[Unit]
Description=Push to Talk (Caps Lock)
After=pipewire.service wireplumber.service
Wants=pipewire.service wireplumber.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 "$D/push-to-talk.py"
Restart=always
RestartSec=2
TimeoutStopSec=3
KillMode=mixed

[Install]
WantedBy=default.target
UNIT

cp "$D/push-to-talk.svg" ~/.local/share/icons/hicolor/scalable/apps/push-to-talk.svg

cat > ~/.local/share/applications/push-to-talk-restart.desktop <<DESK
[Desktop Entry]
Type=Application
Name=Reiniciar Push to Talk
GenericName=Push to Talk
Comment=Finaliza o script de push to talk e inicia uma nova instância
Exec="$D/restart-ptt.sh"
Icon=push-to-talk
Terminal=false
Categories=AudioVideo;Audio;Utility;
Keywords=ptt;push;talk;microfone;mic;caps;
Actions=Stop;

[Desktop Action Stop]
Name=Parar Push to Talk
Exec=systemctl --user stop push-to-talk.service
DESK

gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true
update-desktop-database ~/.local/share/applications 2>/dev/null || true
kbuildsycoca6 >/dev/null 2>&1 || true
systemctl --user daemon-reload
systemctl --user enable --now push-to-talk.service
echo "Instalado. Status: systemctl --user status push-to-talk"
