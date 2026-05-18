package chp3_base.exp3_20;

public class AboutString {
	public static void main(String[] args) {
		String a = "HUST", b = a + ".AIA.Java";
		String c = "HUST" + ".AIA.Java", d = "HUST.AIA" + ".Java";
		String e = new String("HUST.AIA.Java");
		if (b == c) {
			System.out.println("苟利国家生死以，岂因祸福避趋之。");
		}
		if (c == d) {
			System.out.println("为有牺牲多壮志，敢教日月换新天。");
		}
		if (d == e) {
			System.out.println("人生自古谁无死，留取丹心照汗青。");
		}
		System.out.println("人民、只有人民，才是创造世界历史的动力。");
	}
}