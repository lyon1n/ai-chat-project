import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import Login from "./Login";

describe("Login", () => {
  it("shows validation error when fields are empty", async () => {
    render(<Login onLogin={vi.fn()} />);

    await userEvent.click(screen.getAllByRole("button", { name: "登录" }).at(-1));

    expect(screen.getByText("请输入用户名和密码")).toBeInTheDocument();
  });

  it("switches to register mode", async () => {
    render(<Login onLogin={vi.fn()} />);

    await userEvent.click(screen.getAllByRole("button", { name: "注册" })[0]);

    expect(screen.getByText("创建新账号")).toBeInTheDocument();
  });
});
