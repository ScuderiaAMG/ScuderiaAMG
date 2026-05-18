package chp4_oo.exp4_7;
public class MyDate{
    private int day, month, year;
    public MyDate(int day,int month,int year){
    	this.day = day;
    	this.month = month; 
    	this.year = year;
    }	
	public String tomorrow(){
		day = day+1;
		return day+"/"+month+"/"+year;
	}
  public static void main( String[] args){
  	MyDate d = new MyDate(12,4,2009);
  	System.out.println(d.tomorrow());
  }
}
