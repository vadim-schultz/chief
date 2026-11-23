import { describe, expect, it } from "vitest";
import { greet } from "./greeting";

describe("greet", () => {
  it("names the caller", () => {
    expect(greet("Ada")).toBe("Hello, Ada!");
  });
});
