package chp5_advanced.exp5_18;
enum Week {
    SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY 
}
public class EnumValuesTest{
	public static void main( String args[]){
		 
		 for (Week w:Week.values()){
		 	System.out.print ( w.name()+". ");
		 }
		 System.out.println ( );
	}
} 
