using System.Diagnostics;

namespace Checkout;

public sealed class CheckoutService
{
    private static readonly ActivitySource Source = new("Checkout.Business");

    public string Submit(string channel) => channel;

    public string SubmitObserved(string channel)
    {
        using var activity = Source.StartActivity("checkout.submit");
        activity?.SetTag("checkout.channel", channel);
        return channel;
    }
}
