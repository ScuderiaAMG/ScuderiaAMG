package chp5_advanced.exp5_19;
enum Coin2 {
	PENNY(1,CoinColor2.COPPER), 
	NICKEL(5,CoinColor2.NICKEL), 
	DIME(10,CoinColor2.SILVER), 
	QUARTER(25,CoinColor2.SILVER);
	
	private final int value;
	private final CoinColor2 color;
	Coin2(int value, CoinColor2 color) { 
		this.value = value; 
		this.color = color;
	}
	public int value() { return value; }
	public CoinColor2 color(){ return color;} 
}

enum CoinColor2 { COPPER, NICKEL, SILVER }

public class CoinTest2 {
     public static void main(String[] args) {
     	
 // System.out.println(": "+"  "+Coin.PENNY.value());   	
     	for (Coin2 c : Coin2.values())
     	System.out.println(c + ": "+ c.value() +", " + c.color());
    }
}
    	 
   





/* enum Coin {
	PENNY(1), NICKEL(5), DIME(10), QUARTER(25);
	
	private final int value;
	Coin(int value) { this.value = value; }
	public int value() { return value; }
}

public class CoinTest {
     public static void main(String[] args) {
     	
 // System.out.println(": "+"  "+Coin.PENNY.value());   	
     	for (Coin c : Coin.values())
     	System.out.println(c + ": "+ c.value() +"? " +
     	color(c));
    	 }
    	 
    private enum CoinColor2 { COPPER, NICKEL, SILVER }
     
    private static CoinColor2 color(Coin c) {
     switch(c) {
     	case PENNY:
//  	        System.out.println("in switch: "+c+"  "+Coin.PENNY.value());
     		return CoinColor2.COPPER;
     	case NICKEL:
    		return CoinColor2.NICKEL;
     	case DIME: case QUARTER:
     		return CoinColor2.SILVER;
     	default:
     		throw new AssertionError("Unknown coin: " + c);
     }
     }
}

*/