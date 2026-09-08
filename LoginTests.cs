using Xunit;
using Qase.Csharp.Commons.Attributes;

namespace QaseXUnitShowcase;

[Suites("API", "Authentication")]
[Fields("component", "authentication")]
public class LoginTests
{
    [Fact]
    [QaseIds(123)]
    [Title("User can successfully log in with valid credentials")]
    [Fields("priority", "high")]
    [Qase]
    public void UserCanLogin()
    {
        OpenLoginPage();
        EnterCredentials("valid_user", "correct_password");
        ClickLoginButton();
        VerifyDashboard();

        Assert.True(true);
    }

    [Fact]
    [QaseIds(124)]
    [Title("Invalid password shows an error banner")]
    public void InvalidPassword_ShowsError()
    {
        OpenLoginPage();
        EnterCredentials("valid_user", "wrong_password");
        ClickLoginButton();

        Assert.Fail("Error banner was not displayed for invalid password");
    }

    [Fact]
    [Ignore]
    public void ExperimentalFeature_NotYetTracked()
    {
        Assert.True(true);
    }

    [Step]
    public void OpenLoginPage()
    {
    }

    [Step]
    public void EnterCredentials(string username, string password)
    {
    }

    [Step]
    public void ClickLoginButton()
    {
    }

    [Step]
    public void VerifyDashboard()
    {
    }
}
