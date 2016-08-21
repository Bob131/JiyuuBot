namespace JiyuuBot {
    [NoReturn]
    [Diagnostics]
    public void fatal(string message, ...) {
        stderr.printf("** FATAL: ");
        stderr.vprintf(message, va_list());
        stderr.printf("\n");

        Application? app = Application.get_default();
        if (app != null)
            ((!) app).shutdown(); // should block until done

        Process.exit(1);
    }
}
