package lab;

import java.util.ArrayList;
import java.util.List;

public final class CheckoutService {
  public String submit(String channel) throws InterruptedException {
    Thread.sleep(80);
    if ("throw".equals(channel)) throw new IllegalArgumentException("sample failure");
    return channel == null ? "unknown" : channel;
  }

  public int submit(int value) { return value; }

  public static void main(String[] args) throws Exception {
    var service = new CheckoutService();
    List<String> results = new ArrayList<>();
    for (String channel : new String[] {"web", null, "throw"}) {
      try { results.add(service.submit(channel)); }
      catch (IllegalArgumentException expected) { results.add("error"); }
    }
    System.out.println("LAB_RESULT {\"results\":[\"" + String.join("\",\"", results)
        + "\"],\"excluded\":" + service.submit(42) + "}");
  }
}
