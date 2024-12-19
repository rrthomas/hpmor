# latexmk configuration to build HPMOR -*- mode: perl -*-

use Config;
use File::Spec::Functions;

@default_files = (
  'hpmor',
  'hpmor-1', 'hpmor-2', 'hpmor-3', 'hpmor-4', 'hpmor-5', 'hpmor-6',
  'layout/hpmor-dust-jacket-1', 'layout/hpmor-dust-jacket-2',
  'layout/hpmor-dust-jacket-3', 'layout/hpmor-dust-jacket-4',
  'layout/hpmor-dust-jacket-5', 'layout/hpmor-dust-jacket-6',
 );

# Install git hooks for gitinfo2 if not already installed
my $hooks_dir = catdir('.git', 'hooks');
if (-d $hooks_dir) {
  my $checkout = catfile($hooks_dir, 'post-checkout');
  if (!-e $checkout) {
    use File::Copy;
    foreach ('post-checkout', 'post-commit', 'post-merge') {
      my $hook = catfile($hooks_dir, $_);
      copy('post-checkout', $hook) or die "Could not copy `post-checkout' to `$hook'\n";
      my $mode = (stat($hook))[2];
      chmod $mode | 0111, $hook;
    }
    system "git", "checkout"; # Generate .git/gitHeadInfo.gin
  }
}

# Use XeLaTeX (equivalent to command-line -xelatex option)
$xelatex = "xelatex %O \"\\PassOptionsToPackage{$options}{hp-book}\\input{%S}\"" if $options;
my $basedir = curdir();
if (defined($chapter) || defined($chapterfile)) {
  if (defined($chapter)) {
    die "Not in `chapters' directory" if !-d catdir('..', $hooks_dir);
    $basedir = updir();
    $ENV{TEXINPUTS} = ".$Config{path_sep}$basedir$Config{path_sep}";
    $chapterfile = 'hpmor-chapter-' . sprintf('%03d', $chapter);
  } else {
    $chapter = 1;
  }
  $xelatex = "xelatex -jobname=$chapterfile %O \"\\RequirePackage[pdf]{layout/hp-book}\\begin{document}\\setcounter{chapter}{" . ($chapter - 1) . "}\\input{$chapterfile}\\end{document}\"";
}
$pdf_mode = 5;
$postscript_mode = $dvi_mode = 0;

# Make our fonts available to TeX
$ENV{TEXFONTS} = catfile($basedir, 'fonts') . catfile('', '') x 2 . $Config{path_sep};
