public class Main {
    public static void main(String[] args) {
        Robot r = new Robot();
        r.envoyerSimulation(1234.5, 5, 110.0);
        javax.swing.SwingUtilities.invokeLater(() -> new MainFrame());
    }
}