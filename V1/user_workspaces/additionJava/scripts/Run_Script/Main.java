public class Main {
    public static void main(String[] args) {
        // Check if exactly two arguments were provided
        if (args.length != 2) {
            System.out.println("Error: Please provide exactly two numbers.");
            System.out.println("Usage: java Sum <a> <b>");
            return;
        }

        try {
            // Convert the String arguments to integers
            int a = Integer.parseInt(args[0]);
            int b = Integer.parseInt(args[1]);

            // Calculate the sum
            int result = a + b;

            // Print the result
            System.out.println("The sum of " + a + " and " + b + " is: " + result);
        } catch (NumberFormatException e) {
            // Handle cases where the user inputs text instead of numbers
            System.out.println("Error: Both arguments must be valid integers.");
        }
    }
}