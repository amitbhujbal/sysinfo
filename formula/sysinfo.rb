class Sysinfo < Formula
  desc "Simple CLI to show system information"
  homepage "https://github.com/amitbhujbal/sysinfo"
  url "https://github.com/amitbhujbal/sysinfo/archive/refs/tags/v1.0.1.tar.gz"
  sha256 "0de1f6b5601777f44673fbe3a6396785b95d63481d90b677769d58dd00b67f0f"
  license "MIT"

  depends_on "python@3.13"

  def install
    bin.install "sysinfo.py" => "sysinfo"
  end

  test do
    assert_match "System Info", shell_output("#{bin}/sysinfo")
  end
end
