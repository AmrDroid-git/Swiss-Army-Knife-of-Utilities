public class Main {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java Main <a> <b>");
            System.exit(1);
        }

        try {
            double a = Double.parseDouble(args[0]);
            double b = Double.parseDouble(args[1]);

            double result = a + b;

            System.out.println("Sum: " + result);
        } catch (NumberFormatException e) {
            System.out.println("Error: both arguments must be valid numbers.");
            System.exit(1);
        }
    }
}