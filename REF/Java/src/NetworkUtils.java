import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class NetworkUtils {

    public static List<Integer> fetchInstructions(UUID robotUuid) {
        List<Integer> instructions = new ArrayList<>();
        try {
            URL url = new URL("http://10.7.4.225:8000/get_instructions?robot_id=" + robotUuid);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            conn.setRequestMethod("GET");
            conn.setRequestProperty("Accept", "application/json");

            int responseCode = conn.getResponseCode();
            System.out.println(responseCode);
            System.out.println(conn.getResponseMessage());

            // Lire la réponse
            if (conn.getResponseCode() == 200) {
                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {

                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) {
                        response.append(line.trim());
                    }

                    // Exemple de réponse attendue : {"blocks":[2,6,7]}
                    String json = response.toString();
                    int start = json.indexOf("[");
                    int end = json.indexOf("]");
                    if (start != -1 && end != -1 && end > start) {
                        String blocks = json.substring(start + 1, end);
                        String[] nums = blocks.split(",");
                        for (String num : nums) {
                            num = num.trim();
                            if (!num.isEmpty()) {
                                instructions.add(Integer.parseInt(num));
                            }
                        }
                        System.out.println(blocks);
                    }
                }
            } else {
                System.err.println("❌ Erreur serveur : " + conn.getResponseCode());
            }
        } catch (Exception e) {
            System.err.println("❌ Exception réseau : " + e.getMessage());
        }
        return instructions;
    }

    public static void sendSimulationData(UUID robotUuid, double distance, int nbBlocs, double vitesse) {
        try {
            URL url = new URL("http://10.7.4.225:8000/simulation");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "application/json");

            String json = String.format(
                "{\"robot_id\":\"%s\",\"distance_total\":%.2f,\"nb_blocs_prevus\":%d,\"vitesse_cible\":%.2f}",
                robotUuid.toString(), distance, nbBlocs, vitesse
            );

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = json.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            int responseCode = conn.getResponseCode();
            System.out.println("✅ Simulation POST : " + responseCode);

        } catch (Exception e) {
            System.err.println("❌ Erreur POST /simulation : " + e.getMessage());
        }
    }
}