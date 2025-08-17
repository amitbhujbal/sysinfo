class Sysinfo < Formula
  desc "Simple CLI to show system information"
  homepage "https://github.com/amitbhujbal/sysinfo"
  url "https://github.com/amitbhujbal/sysinfo/archive/refs/tags/v1.0.tar.gz"
  sha256 "<PUT_SHA256_HERE>"   # calculate with: shasum -a 256 v1.0.tar.gz
  license "MIT"

  depends_on "python@3.12"

  def install
    bin.install "sysinfo.py" => "sysinfo"
  end

  test do
    assert_match /System Info/, shell_output("#{bin}/sysinfo")
  end
end
