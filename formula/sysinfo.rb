class Sysinfo < Formula
  desc "Simple CLI to show system information"
  homepage "https://github.com/amitbhujbal/sysinfo"
  url "https://github.com/amitbhujbal/sysinfo/archive/refs/tags/v1.1.0.tar.gz"
  sha256 "381be97858434e10a446b369b99063d777a6330789ef075be1485f69d7698fc1"
  license "MIT"

  depends_on "python@3.13"

  def install
    bin.install "sysinfo.py" => "sysinfo"
  end

  test do
    assert_match "System Info", shell_output("#{bin}/sysinfo")
  end
end
