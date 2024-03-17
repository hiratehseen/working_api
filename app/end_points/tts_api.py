# tts_api.py
import bittensor as bt
from classes.tts import TextToSpeechService
import torch
import random
import lib


class TTS_API(TextToSpeechService):
    def __init__(self):
        super().__init__()
        self.current_index = 0  # Initialize the current index
        self.filtered_axons = self._generate_filtered_axons_list()  # Generate the initial list

    def _generate_filtered_axons_list(self):
        """Generate the list of filtered axons."""
        try:
            # Convert the metagraph's UIDs to a list
            uids = self.metagraph.uids.tolist()
            emissions = self.metagraph.E
            bt.logging.debug(f"all the uids and emissions are in this list: {emissions}")

            # Ensure both operands are PyTorch tensors before multiplication
            queryable_axons_mask = torch.tensor(self.metagraph.total_stake >= 0, dtype=torch.float32) * torch.tensor([
                self.metagraph.neurons[uid].axon_info.ip != '0.0.0.0' for uid in uids
            ], dtype=torch.float32)

            # bt.logging.debug(f"Queryable axons mask: {queryable_axons_mask}")
            
            # Filter the UIDs based on the queryable_axons_mask
            # filtered_uids = [uid for uid, queryable in zip(uids, queryable_axons_mask, emissions) if queryable.item()]
            # bt.logging.debug(f"Filtered UIDs: {filtered_uids}")

            # Filter the UIDs based on the queryable_axons_mask
            filtered_uids = [uid for uid, queryable, emission in zip(uids, queryable_axons_mask, emissions) if queryable.item()]
            bt.logging.debug(f"Filtered UIDs: {filtered_uids}")

            # Create a list of tuples (UID, Axon) for the filtered UIDs
            filtered_axons = []
            for uid, queryable in zip(filtered_uids, queryable_axons_mask):
                if queryable.item():
                    axon_info = self.metagraph.neurons[uid].axon_info
                    if axon_info:
                        filtered_axons.append((uid, axon_info))
                    else:
                        bt.logging.warning(f"No axon information found for UID: {uid}")
                else:
                    bt.logging.warning(f"UID {uid} is not queryable.")

            # bt.logging.debug(f"Filtered axons: {filtered_axons}")


        #     # Create a list of tuples (UID, Axon) for the filtered UIDs
        #     filtered_axons = [(uid, self.metagraph.neurons[uid].axon_info) for uid in filtered_uids]
        #     bt.logging.debug(f"Filtered axons: {filtered_axons}")

            return filtered_axons
        except Exception as e:
            print(f"An error occurred while generating filtered axons list: {e}")
            return []



    def get_filtered_axons(self):
        """Get the next item from the filtered axons list."""
        # Regenerate the list if it was exhausted
        if not self.filtered_axons:
            self.filtered_axons = self._generate_filtered_axons_list()
            self.current_index = 0  # Reset the index

        # Get the next item
        if self.filtered_axons:  # Check if the list is not empty
            item_to_return = self.filtered_axons[self.current_index % len(self.filtered_axons)]
            self.current_index += 1  # Increment for next call
            bt.logging.debug(f"Returning axon: {item_to_return}")
            return [item_to_return]
        else:
            return None  # Return None if there are no queryable axons
