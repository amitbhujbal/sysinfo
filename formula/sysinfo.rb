class Sysinfo < Formula
  desc "Simple CLI to show system information"
  homepage "https://github.com/amitbhujbal/sysinfo"
  url "https://github.com/amitbhujbal/sysinfo/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "a8e9b5f0fb1583f1131705b6d7cf89f9705425beb1e5340c0b796d9ccd595a76"
  license "MIT"

  depends_on "python@3.13"

  def install
    bin.install "sysinfo.py" => "sysinfo"
  end

  test do
    assert_match "System Info", shell_output("#{bin}/sysinfo")
  end
end
