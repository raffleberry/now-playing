using System;
using System.Security.Cryptography;
using System.Threading.Tasks;
using Windows.Media.Control;

namespace TestGetCurrentMedia
{
   internal class Program
   {
      public static async Task Main(string[] args)
      {
         var gsmtcsm = await GetSystemMediaTransportControlsSessionManager();
         Gsmtcsm_CurrentSessionChanged(gsmtcsm, null);
         gsmtcsm.CurrentSessionChanged += Gsmtcsm_CurrentSessionChanged;
         Console.ReadLine();
      }
      static string LastString = "";
      private static async void Gsmtcsm_CurrentSessionChanged(GlobalSystemMediaTransportControlsSessionManager sender, CurrentSessionChangedEventArgs args)
      {
         var s = sender.GetCurrentSession();
         if (s != null)
         {
            s.MediaPropertiesChanged += S_MediaPropertiesChanged;
            S_MediaPropertiesChanged(s, null);
            s.PlaybackInfoChanged += S_PlaybackInfoChanged;
            S_PlaybackInfoChanged(s, null);
         }
         //GC.Collect();
      }

      private static void S_PlaybackInfoChanged(GlobalSystemMediaTransportControlsSession sender, PlaybackInfoChangedEventArgs args)
      {
         GlobalSystemMediaTransportControlsSessionPlaybackInfo playbackInfo = sender.GetPlaybackInfo();
         Console.WriteLine(LastString + " => " + playbackInfo.PlaybackStatus);
      }

      private static async void S_MediaPropertiesChanged(GlobalSystemMediaTransportControlsSession sender, MediaPropertiesChangedEventArgs args)
      {
         GlobalSystemMediaTransportControlsSessionMediaProperties mediaProperties = await sender.TryGetMediaPropertiesAsync();
         if (mediaProperties != null)
         {
            string Curr = ($"{mediaProperties.Artist} - {mediaProperties.Title} - {mediaProperties.TrackNumber}");
            if (!Curr.Equals(LastString))
            {
               //Console.WriteLine(Curr);
               LastString = Curr;
               S_PlaybackInfoChanged(sender, null);
            }
         }
      }
      private static async Task<GlobalSystemMediaTransportControlsSessionManager> GetSystemMediaTransportControlsSessionManager() =>
          await GlobalSystemMediaTransportControlsSessionManager.RequestAsync();
   }
}
//https://stackoverflow.com/a/77596316/9133262