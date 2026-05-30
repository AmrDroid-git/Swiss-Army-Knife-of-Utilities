public class Main {
    public static void countdown(String startNumber) {
        try {
            int count = Integer.parseInt(startNumber);

            if (count < 0) {
                System.out.println("Please provide a non-negative number.");
                return;
            }

            while (count >= 0) {
                System.out.println(count);
                if (count > 0) {
                    Thread.sleep(1000);
                }
                count--;
            }

            System.out.println("Countdown complete!");

        } catch (NumberFormatException e) {
            System.out.println("Error: '" + startNumber + "' is not a valid number.");
            System.exit(1);
        } catch (InterruptedException e) {
            System.out.println("Countdown interrupted.");
            Thread.currentThread().interrupt();
        }
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java Main <number>");
            System.exit(1);
        }

        countdown(args[0]);
    }
}