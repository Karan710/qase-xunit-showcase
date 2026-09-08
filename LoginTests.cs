using Xunit;

namespace QaseXUnitShowcase;

public class LoginTests
{
    [Fact]
    public void UserCanLogin()
    {
        Assert.True(true);
    }

    [Fact]
    public void InvalidPassword_ShowsError()
    {
        Assert.True(true);
    }

    [Fact]
    public void ExperimentalFeature_NotYetTracked()
    {
        Assert.True(true);
    }
}
