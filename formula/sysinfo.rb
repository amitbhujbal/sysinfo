class Sysinfo < Formula
  desc "Simple CLI to show system information"
  homepage "https://github.com/amitbhujbal/sysinfo"
  url "https://github.com/amitbhujbal/sysinfo/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "f46e847974fcda94c25b7599a9f3cafaebdab5b5f174f73c62bd83e060695aeb"
  license "MIT"

  depends_on "python@3.13"

  def install
    bin.install "sysinfo.py" => "sysinfo"
  end

  test do
    assert_match "System Info", shell_output("#{bin}/sysinfo")
  end
end
