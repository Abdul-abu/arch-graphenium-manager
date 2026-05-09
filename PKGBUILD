pkgname=arch-graphenium-manager-git
pkgver=0.1.0
pkgrel=1
pkgdesc="Post-install GUI setup for Arch Linux"
arch=('any')
url="https://github.com/Abdul-abu/arch-graphenium-manager"
license=('MIT')
depends=('python' 'python-pyside6')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname::git+https://github.com/Abdul-abu/arch-graphenium-manager.git")
md5sums=('SKIP')

package() {
  cd "$pkgname"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 data/graphenium.desktop "$pkgdir/usr/share/applications/graphenium.desktop"
  install -Dm644 assets/icon.png "$pkgdir/usr/share/icons/hicolor/256x256/apps/graphenium-manager.png"
}