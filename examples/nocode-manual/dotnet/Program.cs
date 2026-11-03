using System.Runtime.CompilerServices;
using System.Text.Json;

namespace Lab;

public sealed class CheckoutService
{
    [MethodImpl(MethodImplOptions.NoInlining)]
    public async Task<string> SubmitAsync(string? channel)
    {
        await Task.Delay(80);
        if (channel == "throw") throw new InvalidOperationException("sample failure");
        return channel ?? "unknown";
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public Task<int> SubmitAsync(int value) => Task.FromResult(value);
}

public static class Program
{
    public static async Task Main()
    {
        var service = new CheckoutService();
        var results = new List<string>();
        foreach (var channel in new string?[] { "web", null, "throw" })
        {
            try { results.Add(await service.SubmitAsync(channel)); }
            catch (InvalidOperationException) { results.Add("error"); }
        }
        Console.WriteLine("LAB_RESULT " + JsonSerializer.Serialize(new {
            results, excluded = await service.SubmitAsync(42)
        }));
    }
}
