#!/bin/sh
systemctl --user disable --now push-to-talk.service 2>/dev/null
rm -f ~/.config/systemd/user/push-to-talk.service \
      ~/.local/share/applications/push-to-talk-restart.desktop \
      ~/.local/share/icons/hicolor/scalable/apps/push-to-talk.svg
systemctl --user daemon-reload
kbuildsycoca6 >/dev/null 2>&1 || true
echo "Desinstalado."
