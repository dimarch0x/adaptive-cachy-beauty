# Maintainer: Dmitry <dimarch0x@gmail.com>
pkgname=adaptive-cachy-beauty-git
pkgver=0.6.0.r0.gdb457d4
pkgrel=1
pkgdesc="Premium Adaptive Material You theming engine for CachyOS and KDE Plasma"
arch=('any')
url="https://github.com/dimarch0x/adaptive-cachy-beauty"
license=('MIT')
depends=('pyside6' 'python-pillow' 'python-colorthief' 'python-requests' 'python-magic' 'python-numpy' 'python-materialyoucolor' 'xorg-xprop')
makedepends=('git' 'python-setuptools')
provides=('adaptive-cachy-beauty')
conflicts=('adaptive-cachy-beauty')
source=('git+https://github.com/dimarch0x/adaptive-cachy-beauty.git')
sha256sums=('SKIP')

pkgver() {
  cd "$srcdir/${pkgname%-git}"
  git describe --long --tags | sed 's/\([^-]*-\)g/r\1/;s/-/./g'
}

package() {
  cd "$srcdir/${pkgname%-git}"
  
  # Install the main python package / files
  install -dm755 "$pkgdir/usr/share/adaptive-cachy-beauty"
  cp -r src resources LICENSE README.md "$pkgdir/usr/share/adaptive-cachy-beauty/"
  
  # Install the executable wrapper
  install -dm755 "$pkgdir/usr/bin"
  cat <<EOF > "$pkgdir/usr/bin/adaptive-cachy-beauty"
#!/bin/bash
python /usr/share/adaptive-cachy-beauty/src/main.py "\$@"
EOF
  chmod +x "$pkgdir/usr/bin/adaptive-cachy-beauty"

  # Install SDDM setup helper
  install -m755 setup_sddm.sh "$pkgdir/usr/bin/adaptive-cachy-sddm-setup"
  
  # Install license
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
