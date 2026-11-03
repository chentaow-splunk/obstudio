package com.example.checkout;

public final class CheckoutService {
  public String submit(Order order) {
    if (order == null) throw new IllegalArgumentException("order required");
    return order.getChannel();
  }

  public String submit(String reference) {
    return reference;
  }

  public static final class Order {
    private final String channel;
    public Order(String channel) { this.channel = channel; }
    public String getChannel() { return channel; }
  }
}
