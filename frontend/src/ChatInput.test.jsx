import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ChatInput from "./ChatInput";

describe("ChatInput", () => {
  it("sends with Enter and keeps Shift+Enter as newline", async () => {
    const onSend = vi.fn().mockResolvedValue(true);
    render(
      <ChatInput
        currentCollection=""
        loading={false}
        onSend={onSend}
        onCancel={vi.fn()}
      />
    );

    const input = screen.getByRole("textbox");
    await userEvent.type(input, "第一行");
    await userEvent.keyboard("{Shift>}{Enter}{/Shift}");
    await userEvent.type(input, "第二行");
    expect(input).toHaveValue("第一行\n第二行");

    await userEvent.keyboard("{enter}");
    expect(onSend).toHaveBeenCalledWith("第一行\n第二行");
  });
});
