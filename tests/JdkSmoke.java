import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import javax.imageio.ImageIO;
import javax.swing.*;

public final class JdkSmoke {
    public static void main(String[] args) throws Exception {
        if (Runtime.version().feature() != 26) throw new AssertionError("Requires JDK 26");
        var temp = Files.createTempDirectory("jdk26-smoke-");
        try {
            var path = temp.resolve("中文.txt");
            Files.writeString(path, "Android Java 26 中文", StandardCharsets.UTF_8);
            if (!Files.readString(path).equals("Android Java 26 中文")) throw new AssertionError("UTF-8");
            var image = new BufferedImage(320, 100, BufferedImage.TYPE_INT_RGB);
            var graphics = image.createGraphics();
            graphics.setColor(Color.WHITE);
            graphics.fillRect(0, 0, 320, 100);
            graphics.setColor(Color.BLACK);
            graphics.drawString("Java 26 中文", 10, 50);
            graphics.dispose();
            var png = temp.resolve("image.png");
            if (!ImageIO.write(image, "png", png.toFile())) throw new AssertionError("PNG writer");
            if (ImageIO.read(png.toFile()).getWidth() != 320) throw new AssertionError("PNG reader");
            var pool = new ArrayList<byte[]>();
            for (int round = 0; round < 80; round++) {
                for (int index = 0; index < 32; index++) pool.add(new byte[128 * 1024]);
                pool.clear();
            }
            Thread worker = Thread.ofPlatform().start(() -> System.out.println("THREAD_OK"));
            worker.join();
            System.out.println("CORE_SMOKE_OK " + System.getProperty("os.arch"));
        } finally {
            try (var entries = Files.list(temp)) {
                for (var entry : entries.toList()) Files.delete(entry);
            }
            Files.delete(temp);
        }
        if (args.length > 0 && args[0].equals("--gui")) {
            if (GraphicsEnvironment.isHeadless()) throw new AssertionError("No X11 display");
            SwingUtilities.invokeAndWait(() -> {
                JFrame frame = new JFrame("JDK 26 Android GUI acceptance");
                frame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
                JPanel panel = new JPanel(new GridLayout(0, 1));
                panel.add(new JLabel("中文字体：请输入文字并点击按钮"));
                JTextField text = new JTextField("Java 26");
                panel.add(text);
                JButton button = new JButton("验证 Swing 点击事件");
                button.addActionListener(event -> {
                    button.setText("已收到：" + text.getText());
                    System.out.println("SWING_INPUT_OK " + text.getText());
                });
                panel.add(button);
                Button awt = new Button("AWT event test");
                awt.addActionListener(event -> System.out.println("AWT_INPUT_OK"));
                panel.add(awt);
                frame.add(panel);
                frame.setSize(540, 320);
                frame.setVisible(true);
                System.out.println("GUI_OPENED_REQUIRES_MANUAL_VISUAL_CHECK");
            });
        }
    }
}
